#!/usr/bin/env python

import sys
import os
import BaseHTTPServer
import json
import psutil
import subprocess
import time
import multiprocessing
import threading
import shutil
import urlparse
from repeat_finder import read_configfile
import cgi

primer3_exe = sys.argv[1]
primer3_dir = sys.argv[2]
myQueue = multiprocessing.Queue()
max_threads = psutil.cpu_count()
# dictionaries for stdit/stdout filenames and file objects
# primary key: worker_ID
worker_stdin = {}
worker_stdout = {}
tmp_file_in = {}
tmp_file_out = {}

# dictionary storing all the running processes
processes = {}
proc_items = {}

# dictionary storing all jobs
jobs = {}




def worker(worker_id):
    global tmp_file
    global jobs
    global proc_items
    global tmp_file_in
    global tmp_file_out
    worker_stdout[worker_id] = os.path.join(primer3_dir, 'worker_output_{}.txt'.format(worker_id))
    worker_stdin[worker_id] = os.path.join(primer3_dir, 'worker_input_{}.txt'.format(worker_id))

    while True:
        if not myQueue.empty():
            proc_items[worker_id] = myQueue.get()
            jobs[proc_items[worker_id]['run_name'][0]] = {'status': 'started'}
            with open(worker_stdin[worker_id], 'w') as tmp_file_in[worker_id]:
                tmp_file_in[worker_id].write(proc_items[worker_id]['primer3_input'][0].strip())
            shutil.copy(worker_stdin[worker_id], primer3_dir + 'in_' + proc_items[worker_id]['run_name'][0] + '.txt')
            with open(worker_stdin[worker_id], 'r') as tmp_file_in[worker_id]:
                with open(worker_stdout[worker_id], 'w') as tmp_file_out[worker_id]:
                    processes[worker_id] = subprocess.Popen(primer3_exe,
                                                            stdout=tmp_file_out[worker_id],
                                                            stdin=tmp_file_in[worker_id])
                    processes[worker_id].wait()
                    processes[worker_id].communicate()[0]
                    tmp_file_out[worker_id].flush()
            shutil.move(worker_stdout[worker_id],
                        os.path.join(primer3_dir + 'out_{}.txt'.format(proc_items[worker_id]['run_name'][0])))
            shutil.move(worker_stdin[worker_id],
                        os.path.join(primer3_dir + 'in_{}.txt'.format(proc_items[worker_id]['run_name'][0])))
            jobs[proc_items[worker_id]['run_name'][0]]['status'] = 'finished'
        else:
            time.sleep(0.5)


class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        output = {}
        # checks if the server is alive
        if self.path == '/test':
            self.send_default_header()
            self.wfile.write('passed')
            self.wfile.write('server is responding')
        # returns the running processes
        elif self.path == '/runningProcesses':
            self.send_default_header()
            # send response:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name'])
                    self.wfile.write(pinfo)
                except psutil.NoSuchProcess:
                    pass

        # returns the CPU utilization and number of cores
        elif self.path == '/cpuInfo':
            self.send_default_header()
            output['CPU Utilization'] = int(psutil.cpu_percent())
            output['CPU Cores'] = int(psutil.cpu_count())
            json.dump(output, self.wfile)
        # returns the number of running primer3 processes
        elif self.path == '/primer3processes':
            self.send_default_header()
            running_primer3 = 0
            output['Primer3 Processes'] = []
            for proc in psutil.process_iter():
                try:
                    if proc.name() == 'primer3_core':
                        running_primer3 += 1
                        output['Primer3 Processes'].append(proc.pid)
                except psutil.NoSuchProcess:
                    output['Running Primer3 processes'] = running_primer3
                    json.dump(output, self.wfile)
        # returns the status of a primer3 job as specified by its run_name
        elif '/job_status' in self.path:
            self.send_default_header()
            parsed = urlparse.urlparse(self.path)
            parameters = urlparse.parse_qs(parsed.query)
            if 'run_name' in parameters.keys():
                run_name = parameters['run_name'][0]
                job_found = False
                if run_name in jobs.keys():
                    job_found = 'status' in jobs[run_name].keys()
                if job_found:
                    output['job_status'] = {run_name: jobs[run_name]['status']}
                else:
                    output['job_status'] = {run_name: 'job not found'}
            json.dump(output, self.wfile)
        # returns the results of a primer3 job as specified by its run_name
        elif '/job_results' in self.path:
            self.send_default_header()
            parsed = urlparse.urlparse(self.path)
            parameters = urlparse.parse_qs(parsed.query)

            if 'run_name' in parameters.keys():
                run_name = parameters['run_name'][0]
                primer3_file = os.path.join(primer3_dir, 'out_{}.txt'.format(run_name))
                if os.path.isfile(primer3_file):
                    with open(primer3_file) as primer3_result:
                        output = primer3_result.read()
            json.dump(output, self.wfile)
        # shuts the server down
        elif self.path == '/shutdown':
            pass

    def parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        if self.path == '/primer3':
            print('Primer3 job request received')
            print(postvars)
            correct_format = True
            if 'run_name' not in postvars.keys() or not 'primer3_input' in postvars.keys():
                print('Missing keys')
                print(postvars.keys())
                correct_format = False
            elif 'SEQUENCE_ID=' not in postvars['primer3_input'][0] or not 'SEQUENCE_TEMPLATE=' in \
                    postvars['primer3_input'][0]:
                print('SEQUENCE_ID=' in postvars['primer3_input'])
                print('SEQUENCE_TEMPLATE=' in postvars['primer3_input'])
                print(postvars['primer3_input'])
                correct_format = False
            if not correct_format:
                print('Primer3 input via POST had a weird format')
                # print(postvars)
                self.send_response(400)
            else:
                jobs[postvars['run_name'][0]] = {'status': 'waiting'}
                myQueue.put(postvars)
                self.send_response(202)  # accepted

    def send_default_header(self):
        self.send_response(200)
        self.send_header("Content-type:", "text/html")
        self.wfile.write("\n")


if __name__ == '__main__':
    # starts worker threads
    for i in range(max_threads):
        t = threading.Thread(target=worker, args=(i,))
        t.daemon = True
        t.start()
        print('worker started')
    # starts server
    server = BaseHTTPServer.HTTPServer(('', 8003), MyRequestHandler)
    server.serve_forever()
