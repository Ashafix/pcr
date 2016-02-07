from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import json
import psutil
from cgi import parse_header
import os
from subprocess import Popen, PIPE
import subprocess
import urllib
import sys
import threading
import Queue as queue #python2.7

threads = []
job_queue = queue.Queue()

class MyRequestHandler (BaseHTTPRequestHandler) :

	def do_GET(self):

		if self.path == '/runningProcesses' :
			#send response code:
			self.send_response(200)
			#send headers:
			self.send_header("Content-type:", "text/html")
			# send a blank line to end headers:
			self.wfile.write("\n")

			#send response:
			for proc in psutil.process_iter():
				try:
					pinfo = proc.as_dict(attrs=['pid', 'name'])
				except psutil.NoSuchProcess:
					pass
				self.wfile.write(pinfo)
		elif self.path == '/cpuInfo':
			#send response code:
			self.send_response(200)
			#send headers:
			self.send_header("Content-type:", "text/html")
			# send a blank line to end headers:
			self.wfile.write("\n")
			cpuInfo = {}
			cpuInfo['CPU Utilization'] = int(psutil.cpu_percent())
			cpuInfo['CPU Cores'] = int(psutil.cpu_count(logical = False))
			json.dump(cpuInfo, self.wfile)
		elif self.path == '/primer3processes':
			running_primer3 = 0
			output = {}
			output['Primer3 Processes'] = []
			for proc in psutil.process_iter():
				try:
					if proc.name() == 'primer3_core':
						running_primer3 += 1
						output['Primer3 Processes'].append(proc.pid)
				except psutil.NoSuchProcess:
					pass

			output['Running Primer3 processes'] = running_primer3
			json.dump(output, self.wfile)
		elif self.path == '/shutdown':
			pass
	def parse_POST(self):
		ctype, pdict = parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		return postvars

	def do_POST(self):
		if self.path == '/primer3':
			input_length = int(self.headers['content-length'])
			primer3_input = self.rfile.read(input_length)
			url = urllib.unquote(primer3_input).decode('utf8')
			url = url.strip()
			print url
			correct_format = True
			if not url.startswith('=') or not url.endswith('='):
				correct_format = False
			elif not 'SEQUENCE_ID=' in url or not 'SEQUENCE_TEMPLATE=' in url:
				correct_format = False
			if correct_format == False:
				print 'Primer3 input via POST had a weird format'
				print url
				self.send_response(400)
			else:
				primer3_input = url[url.find('SEQUENCE_ID=')]
				run_name = url[0:url.find('SEQUENCE_ID=')]
				#waits until at least one CPU is idle
				#while psutil.cpu_percent() * psutil.cpu_count(logical = False) > 80:
				#	time.wait(1)
				#new_thread = threading.Thread(target = primer3_thread, args = primer3_input)
				queue.put(threading.Thread(target = primer3_thread, args=(primer3_input, run_name)))
				for thread in threads:
					thread.daemon = True
					thread.start()
				primer3_thread(primer3_input)
				
				self.send_response(200)

def primer3_thread(primer3_input):
	sys.stdout = open(str(os.getpid()) + ".out", "w")
	#waits until at least one CPU is idle
	while psutil.cpu_percent() * psutil.cpu_count(logical = False) > 80:
		time.wait(1)
	primer3_exe = '/bin/x86_64/primer3_core'
	process = Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
	process.stdin.write(primer3_input)
	primer3_output = process.communicate()[0] + '\n'
	return primer3_output

server = HTTPServer(('', 8003), MyRequestHandler)
server.serve_forever()
