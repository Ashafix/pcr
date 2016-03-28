#!/usr/bin/env python

#Shows all results from previous runs
from subprocess import check_output, STDOUT
from os import path, listdir
from repeat_finder import read_configfile
from time import ctime
import cgi

config_filename = 'batchprimer.conf'
conf_arguments = read_configfile(config_filename)

message = ''
if conf_arguments == '':
	message += 'Configuration file could not be read'
else:
	data_dir = conf_arguments['DATADIR']
	message += '<table style="width:100%"><tr><th>Run ID</th><th>Run Name</th>'
	message += '<th>Results</th><th>Input sequence(s)</th><th>Input BatchDesign parameters</th>'
	message += '<th>Input Primer3 parameters</th><th>Date</th><th></th>'
	message += '</tr>'
	result_files = {}
	filelist = listdir(conf_arguments['DATADIR'])

	#sorts files by date, not pretty but it works
	x = 0
	while  x < len(filelist):
		search_str = '_sequence.fasta'
		if not filelist[x].find(search_str) == 6:
			del filelist[x]
		else:
			x += 1
	filelist.sort(key = lambda x: path.getmtime(conf_arguments['DATADIR'] + x), reverse = True)
	for filename in filelist:
		result_files[filename[0:6]] = {'Sequence':filename}

	for result in result_files:
		if path.isfile(data_dir + result + '_primer3.ini'):
			result_files[result].update({'Primer3':result + '_primer3.ini'})
		if path.isfile(data_dir + result + '_results.txt'):
			result_files[result].update({'Result':result + '_results.txt'})
		if path.isfile(data_dir + result + '_batchprimer.ini'):
			result_files[result].update({'Batchprimer':result + '_batchprimer.ini'})
		if path.isfile(data_dir + result + '_name.txt'):
			result_files[result].update({'Name':result + '_name.txt'})
	url = '<a href="' + '/data/'
	if 'result' in cgi.FieldStorage().keys():
		if len(cgi.FieldStorage()['result'].value) == 6 or len(cgi.FieldStorage()['result'].value) == 20:
			i = 0
			while i < len(filelist):
				if not cgi.FieldStorage()['result'].value in filelist[i]:
					del filelist[i]
				else:
					i += 1
	for filename in filelist:
		result = filename[0:6]
		message += '<tr><td name="test">' + result + '</td>'

		#Name
		message += '<td>' 
		if 'Name' in result_files[result]:
			name_file = open(data_dir+ result_files[result]['Name'], 'r')
			message += name_file.readline()
			name_file.close()
		message += '</td>'

		#Result file
		if 'Result' in result_files[result]:
			message += '<td>' + url + result_files[result]['Result'] + '"> CSV results </a>'
			message += '&nbsp;&nbsp;&nbsp;<a href="../cgi-bin/results2.py?result=' + result + '"> HTML results</a></td>'
		else:
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
		message += '<td>' + ctime(path.getmtime(conf_arguments['DATADIR'] + result + '_sequence.fasta')) + '</td>'
		message += '<td><a href="../cgi-bin/zip_results.py?run=' + result + '"><img src="/images/Farm-Fresh_file_extension_zip.png" '
		message += 'download="' + conf_arguments['DATADIR']+ 'Batchprimer_' + result + '.zip''"></a></td>'
		message += '</tr>\n'
	message += '</form>'
	message += '</table>'
	message += '<br>'
	message += '<br>'
	message += '<br><br><form action="../primer.html"><input type="submit" value="Go back to start page"></form>'

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
