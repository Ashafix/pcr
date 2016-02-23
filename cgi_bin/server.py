#!/usr/bin/env python

#to do
#read file, pass as sequence
#list results

import cgi, os
from repeat_finder import *
from random import SystemRandom
from string import ascii_uppercase, ascii_lowercase, digits
from shutil import copyfile
import boto3
import socket
import urllib2

global data_dir
global run_name

html = ''
sequence_filename = ''
config_filename = 'batchprimer.conf'
#writes a sequence or sequence file to the data directory
def write_sequence(sequence):

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
	legal_header = ascii_lowercase + ascii_uppercase + digits + '_'
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

form = cgi.FieldStorage()
fileitem = form['fastafile']

#checks if the sequence is OK


#checks if the input file is OK


#creates a random name for each run
run_name = ''

while os.path.isfile(run_name) or run_name == '':
	run_name = ''.join(SystemRandom().choice(ascii_uppercase + digits) for _ in range(6))

# Test if a sequence file was uploaded
if fileitem.filename:
	sequence = ''
	for line in fileitem.file.readlines():
		sequence += line
	sequence_filename = write_sequence(sequence)
elif form.getvalue('fastasequence') != '':
	sequence_filename = write_sequence(form.getvalue('fastasequence'))
else:
	html += 'No valid FASTA sequence was provided :(<br>'

input_args = []
input_args.append('-FASTA')
input_args.append(sequence_filename)
input_args.append('-PRIMER3_SETTINGS')
input_args.append(config_args['PRIMER3_SETTINGS'])
input_args.append('-PRIMER3_DIRECTORY')
input_args.append(config_args['PRIMER3_DIRECTORY'])
input_args.append('-PRIMER3_EXE')
input_args.append(config_args['PRIMER3_EXE'])

if int(form.getvalue('maxrepeats')) > 1 and int(form.getvalue('maxrepeats')) < 7:
	input_args.append('-MAXREPEATS')
	input_args.append(form.getvalue('maxrepeats'))
else:
	html += 'Error: Please provide a value between 2 and 6 for the repeat length<br>'
if int(form.getvalue('primerpairs')) > 0 and int(form.getvalue('primerpairs')) < 101:
	input_args.append('-PRIMERPAIRS')
	input_args.append(form.getvalue('primerpairs'))
else:
	html += 'Error: Please provide a value between 1 and 100 for the number of primer pairs<br>'

#write all input files
#batchrun name
if form.getvalue('batchname') != '':
	name_file = open(data_dir + run_name + '_name.txt', 'w')
	name_file.write(form.getvalue('batchname'))
	name_file.close()
#primer3 settings
copyfile(config_args['PRIMER3_SETTINGS'], data_dir + run_name + '_primer3.ini')
#batchprimer settings
batchprimer_file = open(data_dir + run_name + '_batchprimer.ini', 'w')
for input_arg in input_args:
	batchprimer_file.write(str(input_arg) + '\n')
batchprimer_file.close()

if not 'Error: ' in html:
	if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
		if not start_remote_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT'], 120):
			html += "Error: Compute server could not be started.<br>"

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
		if instance.private_dns_name != hostname and compute_host == '':
			compute_host = instance.id
			#get the base hostname
			config_args['SERVERNAME'] = instance.private_dns_name.split('.')[0] 
			remoteserver_url = 'http://' + instance.public_dns_name
			if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
				html += '<br>Server start was succesful, but gfServer does not respond<br>'

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
	html += reply + '<br>'
	if not 'CPU' in reply:
		html += 'Error: Rest server is not responding'

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

	batchprimer_result = start_repeat_finder(False, input_args)
	result_file = open(data_dir + run_name + '_results.txt', 'w')
	if batchprimer_result != '':
		result_file.write(batchprimer_result)
	else:
		result_file.write('FAILED')
	#html += '<meta http-equiv="refresh" content="1;url=results.py">\n'
	html += '<script type="text/javascript">\n'
	#html += 'window.location.href = "results.py"\n'
	html += '</script><title>Page Redirection</title></head><body>'
	html += 'You should be redirected automatically, if not go to the <a href="results.py">results</a>'
	html += '</body></html>'

	result_file.close()
elif sequence_filename:
	html += 'Server is not ready, please try again later.<br>'

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (html,)
