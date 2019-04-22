#!/usr/bin/env python


import json
import cgi
import urllib2
print
parameters = cgi.FieldStorage()
run_name = ''
remote_ip = ''
if 'run_name' in parameters.keys():
    run_name = parameters['run_name']
if 'remote_ip' in parameters.keys():
    remote_ip = parameters['remote_ip']
try:
    resp = urllib2.urlopen('http://{0}:8004/job_result?run_name={1}'.format(remote_ip, run_name)).read()
    print(resp)
except:
    pass

