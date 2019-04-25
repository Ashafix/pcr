#!/usr/bin/env python

import BaseHTTPServer
import json
import psutil
import cgi
import urlparse
import socket
import urllib2
import repeat_finder
import boto3

ip_list = []
own_ip = ''


def get_own_ip():
    try:
        # AWS internal URL
        own_ip = urllib2.urlopen("http://169.254.169.254/latest/meta-data/public-ipv4").read()
    except:
        own_ip = None
    if own_ip is None:
        # get own URL
        own_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                  [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    return own_ip


def send_header(target):
    target.send_response(200)
    target.send_header("Content-type:", "text/html")
    target.send_header('Access-Control-Allow-Origin', '*')
    target.end_header()


class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):


    def do_GET(self):
        output = dict()
        # checks if the server is alive
        if self.path == '/test':
            send_header(self)
            self.wfile.write('passed')
            self.wfile.write('server is responding')
        # returns the running processes
        elif self.path == '/runningProcesses':
            self.send_response(200)
            self.send_header("Content-type:", "text/html")
            self.wfile.write("\n")

            # send response:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name'])
                    self.wfile.write(pinfo)
                except psutil.NoSuchProcess:
                    pass

        # returns the CPU utilization and number of cores
        elif self.path == '/cpuInfo':
            send_header(self)
            output['CPU Utilization'] = int(psutil.cpu_percent())
            output['CPU Cores'] = int(psutil.cpu_count())
            json.dump(output, self.wfile)
        # returns the own IP address
        elif self.path == '/myIP':
            send_header(self)
            output['IP'] = own_ip
            json.dump(output, self.wfile)
        elif self.path == '/refreshIPs':
            aws = repeat_finder.read_aws_conf()
            session = boto3.session.Session(aws_access_key_id=aws['aws_access_key_id'],
                                            aws_secret_access_key=aws['aws_secret_access_key'],
                                            region_name=aws['region_name'])
            ec2 = session.resource('ec2')
            instances = ec2.instances.all()

            for instance in instances:
                self.ip_list.append(instance.public_ip_address)

        elif '/job_result' in self.path:
            send_header(self)
            parsed = urlparse.urlparse(self.path)
            parameters = urlparse.parse_qs(parsed.query)
            run_name = ''
            remote_ip = ''
            if 'run_name' in parameters.keys():
                run_name = parameters['run_name'][0]
            if 'remote_ip' in parameters.keys():
                remote_ip = parameters['remote_ip'][0]
            if not remote_ip in ip_list:
                json.dump({'status': 'forbidden'}, self.wfile)

            try:
                resp = urllib2.urlopen('http://{0}:8004/job_result?run_name={1}'.format(remote_ip, run_name)).read()
                print(resp)
                json.dump(resp, self.wfile)
            except:
                json.dump({'status': 'unknown'}, self.wfile)
        # shuts the server down
        elif self.path == '/shutdown':
            pass

    def parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = dict()
        return postvars

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = dict()
        # add job type to postvars


def main():
    own_ip = get_own_ip()
    print(own_ip)
    # starts server
    server = BaseHTTPServer.HTTPServer(('', 8003), MyRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()