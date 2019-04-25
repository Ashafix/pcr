#!/usr/bin/env python

import sys
import os
import json
import psutil
import argparse
import subprocess
import time
import multiprocessing
import threading
import shutil
import cgi
if sys.version_info < (3, 0):
    import BaseHTTPServer
    import urlparse
    encode = lambda x: x
else:
    import http.server as BaseHTTPServer
    import urllib.parse as urlparse
    encode = lambda x: bytes(x, encoding='utf-8')
myQueue = multiprocessing.Queue()
# dictionaries for stdin/stdout filenames and file objects
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


def worker(worker_id, primer3_dir, primer3_exe):
    worker_stdout[worker_id] = os.path.join(primer3_dir, 'worker_output_{}.txt'.format(worker_id))
    worker_stdin[worker_id] = os.path.join(primer3_dir, 'worker_input_{}.txt'.format(worker_id))

    while True:
        if myQueue.empty():
            time.sleep(0.5)
            continue
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
                processes[worker_id].communicate()
                tmp_file_out[worker_id].flush()
        shutil.move(worker_stdout[worker_id],
                    os.path.join(primer3_dir + 'out_{}.txt'.format(proc_items[worker_id]['run_name'][0])))
        shutil.move(worker_stdin[worker_id],
                    os.path.join(primer3_dir + 'in_{}.txt'.format(proc_items[worker_id]['run_name'][0])))
        jobs[proc_items[worker_id]['run_name'][0]]['status'] = 'finished'


class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_default_header()
        # checks if the server is alive
        if self.path == '/test':
            self.wfile.write(encode('passed<br/>'))
            self.wfile.write(encode('server is responding'))
        # returns the running processes
        elif self.path == '/runningProcesses':
            # send response:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name'])
                    self.wfile.write(pinfo)
                except psutil.NoSuchProcess:
                    pass

        # returns the CPU utilization and number of cores
        elif self.path == '/cpuInfo':
            output = {'CPU Utilization': int(psutil.cpu_percent()),
                      'CPU Cores': int(psutil.cpu_count())}
            resp = json.dumps(output)
            self.wfile.write(encode(resp))
        # returns the number of running primer3 processes
        elif self.path == '/primer3processes':
            output = {'Primer3 Processes': [],
                      'running_primer3': 0}
            for proc in psutil.process_iter():
                try:
                    if proc.name() == 'primer3_core':
                        output['running_primer3'] += 1
                        output['Primer3 Processes'].append(proc.pid)
                except psutil.NoSuchProcess:
                    pass
            resp = json.dumps(output)
            self.wfile.write(encode(resp))
        # returns the status of a primer3 job as specified by its run_name
        elif '/job_status' in self.path:
            parsed = urlparse.urlparse(self.path)
            parameters = urlparse.parse_qs(parsed.query)
            output = {}
            if 'run_name' in parameters.keys():
                run_name = parameters['run_name'][0]
                job_found = False
                if run_name in jobs.keys():
                    job_found = 'status' in jobs[run_name].keys()
                if job_found:
                    output['job_status'] = {run_name: jobs[run_name]['status']}
                else:
                    output['job_status'] = {run_name: 'job not found'}
            resp = json.dumps(output)
            self.wfile.write(encode(resp))
        # returns the results of a primer3 job as specified by its run_name
        elif '/job_results' in self.path:
            parsed = urlparse.urlparse(self.path)
            parameters = urlparse.parse_qs(parsed.query)
            output = ''
            if 'run_name' in parameters.keys():
                run_name = parameters['run_name'][0]
                primer3_file = os.path.join(self.primer3_dir, 'out_{}.txt'.format(run_name))
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
            postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
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
                self.send_response(400)
            else:
                jobs[postvars['run_name'][0]] = {'status': 'waiting'}
                myQueue.put(postvars)
                self.send_response(202)  # accepted

    def send_default_header(self):
        self.send_response(200)
        self.send_header("Content-type:", "text/html")
        self.end_headers()


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('primer3_dir')
    parser.add_argument('primer3_exe')
    parser.add_argument('--port', default=8003, type=int)
    return parser.parse_args(args)


def main(args):
    args = parse_args(args)
    # starts worker threads
    max_threads = psutil.cpu_count()

    for i in range(max_threads):
        t = threading.Thread(target=worker, args=(i, args.primer3_dir, args.primer3_exe))
        t.daemon = True
        t.start()
        print('worker started')
    # starts server
    MyRequestHandler.primer3_dir = args.primer3_dir
    server = BaseHTTPServer.HTTPServer(('', args.port), MyRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
