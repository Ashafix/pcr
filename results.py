#!/usr/bin/env python

#Shows all results from previous runs
from subprocess import check_output, STDOUT
from os import path, listdir
from repeat_finder import read_configfile

conf_arguments = read_configfile()

message = ''
if conf_arguments == '':
	message += 'Configuration file could not be read'
	
else:
	data_dir = conf_arguments['DATADIR']
	message += '<table style="width:100%"><tr><th>Run ID</th><th>Run Name</th><th>Input sequence(s)</th><th>Input BatchDesign parameters</th><th>Input Primer3 parameters</th></tr>'
	result_files = {}
	for filename in listdir(conf_arguments['DATADIR']):
		if filename.endswith('_sequence.fasta'):
			result_files[filename[0:6]] = {'Sequence':filename}
			
	for result in result_files:
		if path.isfile(data_dir + result + '_primer3.ini'):
			result_files[result].update({'Primer3':result + '_primer3.ini'})
		if path.isfile(data_dir + result + '_results.txt'):
			result_files[result].update({'Result':result + '_results.txt'})
		if path.isfile(data_dir + result + '_batchprimer.ini'):
			result_files[result].update({'Batchprimer':result + '_batchprimer.ini'})

url = '<a href="' + '/data/'
for result in result_files:
	message += '<tr><td>' + result + '</td>'
	message += '<td></td>'
	message += '<td>' + url + result + '_sequence.fasta">' + result + '_sequence.fasta' + '</a></td>'
	if 'Batchprimer' in result_files[result]:
		message += '<td>' + url + result_files[result]['Batchprimer'] + '">' + result_files[result]['Batchprimer'] + '</a></td>'
	else:
		message += '<td></td>'
	if 'Primer3' in result_files[result]:
		message += '<td>' + url + result_files[result]['Primer3'] + '">' + result_files[result]['Primer3'] + '</a></td>'
	else:
		message += '<td></td>'
	message += '</tr>'

message += '</table>'
message += '<br>'
message += '<br>'
message += '<br><br><form action="../primer.html"> <input type="submit" value="Go back to start page"></form>'

	
print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
