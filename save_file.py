#!/usr/bin/env python
import cgi, os
import cgitb; cgitb.enable()
from subprocess import Popen, PIPE
import subprocess
import sys
import os
from repeat_finder import *

form = cgi.FieldStorage()

# A nested FieldStorage instance holds the file
fileitem = form['fastafile']

# Test if the file was uploaded
#message = "oops"
#message = str(form)

message = ''

# Test if the file was uploaded
if "Submit job" in form:
	if fileitem.filename:
		# strip leading path from file name to avoid directory traversal attacks
		fn = os.path.basename(fileitem.filename)
		message = 'The file "' + fn + '" was uploaded successfully'
	elif form.getvalue('fastasequence') == '':
		message += 'No sequence was provided :('
	else:
		message += form.getvalue('maxrepeats') + '\n'
		message += form.getvalue('primerpairs') + '\n'
		message += form.getvalue('maxsimilarity') + '\n'
		message += form.getvalue('fastasequence')  + '\n'
		message += form.getvalue('nested') + '\n'
		message += str(test_server('/home/ashafix/bin/x86_64/gfServer', 'backtrack3', 33334))
	
	input_args = []
	input_args.append('-FASTA')
	input_args.append('/home/ashafix/Desktop/pcr/har2b.txt')
	input_args.append('-PRIMER3_SETTINGS')
	input_args.append('/home/ashafix/Desktop/pcr/primer3_settingsDavid.txt')
	input_args.append('-PRIMER3_DIRECTORY')
	input_args.append('/tmp/')
	input_args.append('-PRIMER3_EXE')
	input_args.append('/home/ashafix/Desktop/pcr/primer3_core')
	input_args.append('-SERVERNAME')
	input_args.append('backtrack3')
	input_args.append('-SERVERPORT')
	input_args.append('33334')
	input_args.append('-MAXREPEATS')
	input_args.append('2')
	input_args.append('-PRIMERPAIRS')
	input_args.append('2')
	input_args.append('-GFSERVER')
	input_args.append('/home/ashafix/bin/x86_64/gfServer')
	input_args.append('-GFPCR')
	input_args.append('/home/ashafix/bin/x86_64/gfPcr')

	
	message += ' '.join(input_args) + '\n'
	if test_server('/home/ashafix/bin/x86_64/gfServer', 'backtrack3', 33334):
		message += start_repeat_finder(False, input_args)

elif "Test server status" in form:
	message = "gfServer is "
	if test_server("/home/ashafix/bin/x86_64/gfServer", "backtrack3", 33334):
		message += "up and running<br>"
	else:
		message += "IS NOT running<br>"
	primer3_exe = "/home/ashafix/Desktop/pcr/primer3_core"
	message += 'Primer3 executable'
	if os.path.isfile(primer3_exe):
		message += ' is found<br>'
	else:
		message += ' IS NOT found<br>'
	
print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
