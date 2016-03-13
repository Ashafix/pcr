#!/usr/bin/env python

import cgi, os
from repeat_finder import *
from random import SystemRandom
from string import ascii_uppercase, ascii_lowercase, digits
from shutil import copyfile
import boto3
import socket
import urllib2
import threading
from time import sleep
from multiprocessing import Queue
from threading import Thread

global data_dir
global run_name

html = ''
sequence_filename = ''
config_filename = 'batchprimer.conf'
input_args = []
cgi_args = ['batchname', 'maxrepeats', 'primerpairs', 'maxsimilarity', 'nested', 'fastasequence']

#dictionary with all the jobs, key = worker_id
proc_items = {}
#queue storing jobs, list: ID, input_parameters
myQueue = Queue()
#dictionary with batchprimer3 results, key: job number
worker_results = {}

#dictionary with 'number of CPUs':extension
server_extensions = {2:'c4.large', 8:'c4.2xlarge'}

header = """\
Content-Type: text/html\n
<html><body>
<p>
"""
end = """\
</p>
</body></html>
"""
html_code = ''

print (header)
print ('Your job was submitted. Please be patient....<br><br>\n')
sys.stdout.flush()

def worker(worker_id):

	global jobs
	global proc_items
	global tmp_file_in
	global tmp_file_out
	worker_stdout[worker_id] = primer3_dir + 'worker_output_' + str(worker_id) + '.txt'
	worker_stdin[worker_id] = primer3_dir + 'worker_input_' + str(worker_id) + '.txt'

	while True:
		if not myQueue.empty():
			proc_items[worker_id] = myQueue.get()
			worker_results[proc_items[worker_id][0]] = start_repeat_finder(False, proc_items[worker_id][1])
			
		else:
			sleep(0.5)


class dots(threading.Thread):
	"""
	a background thread for printing dots
	"""
	def __init__(self, dot):
		threading.Thread.__init__(self)
		self.runnable = dot
		self.daemon = True
	def run(self):
		self.runnable()

def dot():
	"""
	prints a dot every second
	"""
	global print_dots
	while print_dots:
		html_output('.')
		sleep(1)


def cgi_result(data, environ):
	"""fakes a cgi result
	data: input data
	environ: environment variables
	"""
	fake_stdin = StringIO(data)
	fake_stdin.seek(0)
	fake_form = cgi.FieldStorage(fp = fake_stdin, environ = environ)	
	return fake_form

def html_output(new_line):
	"""
	generates dynamic html output
	"""
	global html_code
	html_code += new_line
	html_output = header + html_code + end
	sys.__stdout__.write(new_line + '\n')
	sys.__stdout__.flush()

#writes a sequence or sequence file to the data directory
def write_sequence(sequence, index = ''):

	if index != '':
		fasta_filename = data_dir + run_name + '_' + str(index)
		fasta_filename += '_sequence.fasta' 
	else:
		fasta_filename = data_dir + run_name + '_sequence.fasta' 
	if sequence != '':
		fasta_file = open(fasta_filename, 'w')
		sequence = clean_sequence(sequence)
		fasta_file.write(sequence)
		fasta_file.close()
	else:
		return ''
	return fasta_filename


def clean_sequence(sequence):
	"""
	cleans a FASTA nucleotide sequence
	"""
	new_sequence = ''
	nucleotides = 'ATGC'
	legal_header = ascii_lowercase + ascii_uppercase + digits + '_=:\'+- '
	for line in sequence.splitlines():
		if line.startswith('>'):
			new_sequence += '>'
			new_sequence += ''.join(header for header in line if header in legal_header)
			new_sequence += '\n'
		else:
			line = line.upper()
			new_sequence += ''.join(nuc for nuc in line if nuc in nucleotides)
			new_sequence += '\n'
	return new_sequence

def correct_fasta (sequence):
	"""
	checks if a FASTA file is correct
	"""
	header = False #indicates whether a header was found
	sequence = sequence.strip()
	if not sequence.startswith('>'):
		return False
	fasta_lines = sequence.split('\n')
	if len(fasta_lines) < 2:
		return False
	for fasta_line in fasta_lines:
		if fasta_line.startswith('>'):
			if header == True:
				return False
			header = True
		else:
			if header == False:
				return False
			header = False
			fasta_line = fasta_line.upper()
			if not all(nuc in ('ATGC\n\r') for c in fasta_line):
				return False
	return True
config_args = read_configfile(config_filename)
data_dir = config_args['DATADIR']

#standard use via web
if len(sys.argv) == 1:
	form = cgi.FieldStorage()
#for debugging and unit testing
elif len(sys.argv) > len(cgi_args):
	from StringIO import StringIO
	formdata = ''
	for i in range(0, len(cgi_args)):
		formdata += '---123\nContent-Disposition: form-data; name="'
		formdata += cgi_args[i] + '"\n\n'
		formdata += sys.argv[1 + i] + '\n'
	formdata += '---123\nContent-Disposition: form-data; name="fastafile"; filename=""\nContent-Type: text/plain\n'
	formdata_environ = {
		'CONTENT_LENGTH': str(len(formdata)),
		'CONTENT_TYPE': 'multipart/form-data; boundary=-123',
		'QUERY_STRING': '',
		'REQUEST_METHOD': 'POST',
	}
	form = cgi_result(formdata, formdata_environ)

try:
	fasta_fileitem = form['fastafile']
	primer3_fileitem = form['primer3file']
except:
	html += 'Error: Not started via a proper CGI form'
	html_output('Error: Not started via a proper CGI form')
	sys.exit()

nested = -1
try:
	if form.getvalue('nested'):
		nested = form.getvalue('nested')
except:
	html += 'Not started via a proper CGI form - Nested checkbox is missing'
	html_output('Not started via a proper CGI form - Nested checkbox is missing')
#checks if the sequence is OK



#checks if the input file is OK


#creates a random name for each run
run_name = ''
if form.getvalue('private'):
	#create a long runname which is not shown in results
	msg = '<br>Your result will not be public and can only be accessed via the direct link. If you lose this link, you cannot access your results.<br>'
	html += msg
	html_output(msg)
	while os.path.isfile(run_name) or run_name == '':
		run_name = ''.join(SystemRandom().choice(ascii_uppercase + digits) for _ in range(24))
else:
	while os.path.isfile(run_name) or run_name == '':
		run_name = ''.join(SystemRandom().choice(ascii_uppercase + digits) for _ in range(6))

# Test if a sequence file was uploaded
sequence = ''
if fasta_fileitem.filename:
	for line in fasta_fileitem.file.readlines():
		sequence += line
elif form.getvalue('fastasequence') != '':
	sequence = form.getvalue('fastasequence')
else:
	msg = 'Error: No valid FASTA sequence was provided<br>'
	html += msg
	html_output(msg)

#Test if a primer3 settings file was uploaded
input_args.append('-PRIMER3_SETTINGS')
if primer3_fileitem.filename:
	primer3_settings = primer3_fileitem.file.read()
	primer3_filename = data_dir + run_name + '_primer3.ini'
	primer3_file = open(primer3_filename, 'w')
	primer3_file.write(primer3_settings)
	primer3_file.close()
	input_args.append(primer3_filename)
else:
	input_args.append(config_args['PRIMER3_SETTINGS'])

if sequence.count('>') > 48:
	msg = "Error: Please don't submit more than 48 sequences at once. Feel free to contact us at maximili.peters@mail.huji.ac.il to discuss further options.<br>"
	html += msg
	html_output(msg)
else:
	#finds the suitable AWS instance type depending on the number of jobs
	server_extension = ''
	for key in sorted(server_extensions.iterkeys()):
		if (sequence.count('>') / int(key)) > 5:
			server_extension = server_extensions[key]
			config_args['MAXTHREADS'] = key
	if server_extension == '':
		server_extension = server_extensions[2]

sequence = sequence.strip()
sequence_filename = write_sequence(sequence)
input_args.append('-PRIMER3_DIRECTORY')
input_args.append(config_args['PRIMER3_DIRECTORY'])
input_args.append('-PRIMER3_EXE')
input_args.append(config_args['PRIMER3_EXE'])
input_args.append('-NESTED')
input_args.append(nested)
input_args.append('-MAXTHREADS')
input_args.append(config_args['MAXTHREADS'])

if int(form.getvalue('maxrepeats')) > 1 and int(form.getvalue('maxrepeats')) < 7:
	input_args.append('-MAXREPEATS')
	input_args.append(form.getvalue('maxrepeats'))
else:
	html += 'Error: Please provide a value between 2 and 6 for the repeat length<br>'
	html_output('Error: Please provide a value between 2 and 6 for the repeat length<br>')
if int(form.getvalue('primerpairs')) > 0 and int(form.getvalue('primerpairs')) < 101:
	input_args.append('-PRIMERPAIRS')
	input_args.append(form.getvalue('primerpairs'))
else:
	html += 'Error: Please provide a value between 1 and 100 for the number of primer pairs<br>'
	html_output('Error: Please provide a value between 1 and 100 for the number of primer pairs<br>')

#write all input files
#batchrun name
if form.getvalue('batchname') != '':
	name_file = open(data_dir + run_name + '_name.txt', 'w')
	name_file.write(form.getvalue('batchname'))
	name_file.close()
#primer3 settings
if not primer3_fileitem.filename:
	copyfile(config_args['PRIMER3_SETTINGS'], data_dir + run_name + '_primer3.ini')
#batchprimer settings
batchprimer_file = open(data_dir + run_name + '_batchprimer.ini', 'w')
for input_arg in input_args:
	batchprimer_file.write(str(input_arg) + '\n')
batchprimer_file.close()

if not 'Error: ' in html:
	if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
		html_output('Remote server will be started now. This might take a minute or two.<br>')
		new_servername = start_remote_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT'], 120, server_extension)
		if  new_servername == '':
			html += 'Error: Compute server could not be started.<br><br>'
			html_output('Error: Compute server could not be started.<br><br>')
		else:
			config_args['SERVERNAME'] = new_servername
			html_output('Remote server is running now.<br><br>')

remoteserver_url = ''

if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
	#check for new DNS of AWS instance and replace old name
	aws = read_aws_conf()
	session = boto3.session.Session(aws_access_key_id = aws['aws_access_key_id'], 
		aws_secret_access_key = aws['aws_secret_access_key'], 
		region_name = aws['region_name'])
	ec2 = session.resource('ec2')
	instances = ec2.instances.all()
	hostname = socket.gethostbyaddr(socket.gethostname())[0]
	compute_host = ''
	for instance in instances:
		instance_name = ''
		for tag in instance.tags:
			if 'Value' in tag:
				if 'Key' in tag.keys() and 'Value' in tag.keys():
					if tag['Key'] == 'Name':
						instance_name = tag['Value']
		if instance_name == config_args['SERVERNAME'] and compute_host == '':
			compute_host = instance.id
			#get the base hostname
			config_args['SERVERNAME'] = instance.private_dns_name.split('.')[0] 
			remoteserver_url = 'http://' + instance.public_dns_name
			if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
				html += '<br>Server start was successful, but gfServer does not respond<br>'
				html_output('<br>Server start was successful, but gfServer does not respond<br>')

if remoteserver_url != '':
	#checks if the REST server is responding
	url = remoteserver_url + ':8003/cpuInfo'
	reply = ''
	try:
		req = urllib2.Request(url, )
		response = urllib2.urlopen(req)
		reply = str(response.read())
	except:
		pass
	if not 'CPU' in reply:
		html += '<br>Rest server URL: ' + remoteserver_url
		html_output('<br>Rest server URL: ' + remoteserver_url)
		html += '<br>Error: Rest server is not responding'
		html_output('<br>Error: Rest server is not responding')
else:
	html += '<br>Error: Remote server has no URL<br>'
	html_output('<br>Error: Remote server has no URL<br>')

if test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']) and \
	sequence_filename and \
	not 'Error: ' in html:

	input_args.append('-SERVERNAME')
	input_args.append(config_args['SERVERNAME'])
	input_args.append('-SERVERPORT')
	input_args.append(config_args['SERVERPORT'])
	input_args.append('-GFSERVER')
	input_args.append(config_args['GFSERVER'])
	input_args.append('-GFPCR')
	input_args.append(config_args['GFPCR'])
	input_args.append('-DATADIR')
	input_args.append(config_args['DATADIR'])
	input_args.append('-REMOTESERVER')
	input_args.append(remoteserver_url)
	input_args.append('-RUNNAME')
	input_args.append(run_name)
	html_output('Hemi-NeSTR was just started. It will take about two minutes per sequence batch.<br>')
	html_output('<br><a target="_blank" href="/data/' + run_name + '_results.txt">Your results will be here</a><br>')

	result_file = open(data_dir + run_name + '_results.txt', 'w')
	result_file.close()
	finished = False

	sub_seqs = []
	offset = 0

	#needed to deal with different sequence formats (single or multiple)
	sequence = ' ' + sequence

	#splits multiple sequences into a list of sequences
	while offset != -1:
		offset = sequence.find('>', offset + 1)
		if offset != -1:
			sub_seqs.append(sequence[offset:sequence.find('>', offset + 1)].strip())

	input_args.append('-FASTA')
	base_args = input_args[:]
	
	#starts the background thread for printing dots
	print_dots = False
	thread = dots(dot)
	thread.start()
	html_output('<br>a batch of jobs was started<br>')
	for i in range(0, int(config_args['MAXTHREADS'])):
		#starts worker threads
		t = Thread(target = worker, args = (i,))
		t.daemon = True
		t.start()
	for i in range(0, len(sub_seqs)):
		input_args = base_args[:]
		sequence = ''
		sequence += sub_seqs[i] + '\n'
		sequence_filename = write_sequence(sequence, str(i))
		input_args.append(sequence_filename)
		myqueue.put([i, input_args])

	while not myQueue.empty():
		print_dots = True
		sleep(0.5)

	html_output('<br>a batch of jobs just finished<br>')
	print_dots = False
	result_file = open(data_dir + run_name + '_results.txt', 'a')
	if batchprimer_result != '':
		result_file.write(str(worker_results))
	else:
		result_file.write('FAILED\n')
	result_file.close()

	html_output('<br>Your job is finished and the link above should work now.<br>')
	#print ('<meta http-equiv="refresh" content="1;url=results.py">\n'
	#html += '<script type="text/javascript">\n'
	#html_output('<script type="text/javascript">\n')
	#print ('window.location.href = "results.py"\n'
	#html += '</script><title>Page Redirection</title></head><body>'
	#html_output('</script><title>Page Redirection</title></head><body>')
	#html += 'You should be redirected automatically, if not go to the <a href="results.py">results</a>'
	#html_output('You should be redirected automatically, if not go to the <a href="results.py">results</a>')
	html += '</body></html>'
	html_output('</body></html>')

	result_file.close()
elif sequence_filename:
	html += 'Server is not ready, please try again later.<br>'
	html_output('Server is not ready, please try again later.<br>')

print (end)
