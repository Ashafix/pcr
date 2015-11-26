#!/usr/bin/env python

#to do
#read file, pass as sequence
#name runs, list results
#check if server is busy
#

import cgi, os
import cgitb; cgitb.enable()
from subprocess import Popen, PIPE
import subprocess
import sys
import os
from repeat_finder import *
from random import SystemRandom
from string import ascii_uppercase
from string import ascii_lowercase
from string import digits
from shutil import copyfile

global data_dir
global run_name

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
		pass
	return fasta_filename

#cleans a fasta nucleotide sequence
def clean_sequence(sequence):
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

config_args = read_configfile()
data_dir = config_args['DATADIR']

form = cgi.FieldStorage()
fileitem = form['fastafile']

run_name = ''.join(SystemRandom().choice(ascii_uppercase + digits) for _ in range(6))
while os.path.isfile(run_name):
	run_name = ''.join(SystemRandom().choice(ascii_uppercase + digits) for _ in range(6))

# Test if the file was uploaded
if fileitem.file:
	#strip leading path from file name to avoid directory traversal attacks
	sequence = ''
	for line in fileitem.file.readlines():
		sequence += line
	sequence_filename = write_sequence(sequence)
elif form.getvalue('fastasequence') != '':
	sequence_filename = write_sequence(form.getvalue('fastasequence'))
else:
	message += 'No sequence was provided :('




input_args = []
input_args.append('-FASTA')
input_args.append(sequence_filename)
input_args.append('-PRIMER3_SETTINGS')
input_args.append(config_args['PRIMER3_SETTINGS'])
input_args.append('-PRIMER3_DIRECTORY')
input_args.append(config_args['PRIMER3_DIRECTORY'])
input_args.append('-PRIMER3_EXE')
input_args.append(config_args['PRIMER3_EXE'])
input_args.append('-SERVERNAME')
input_args.append(config_args['SERVERNAME'])
input_args.append('-SERVERPORT')
input_args.append(config_args['SERVERPORT'])
input_args.append('-MAXREPEATS')
input_args.append('2')
input_args.append('-PRIMERPAIRS')
input_args.append('2')
input_args.append('-GFSERVER')
input_args.append(config_args['GFSERVER'])
input_args.append('-GFPCR')
input_args.append(config_args['GFPCR'])
input_args.append('-DATADIR')
input_args.append(config_args['DATADIR'])

#write all input files
#primer3 settings
copyfile(config_args['PRIMER3_SETTINGS'], data_dir + run_name + '_primer3.ini')
#batchprimer settings

# Test if the file was uploaded
#message = "oops"
#message = str(form)

message = ''

#message += ' '.join(input_args) + '\n'
if test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
	batchprimer_result = start_repeat_finder(False, input_args)
	result_file = open(data_dir + run_name + '_results.txt', 'w')
	if batchprimer_result != '':
		result_file.write(batchprimer_result)
	else:
		result_file.write('FAILED')
	result_file.close()

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
