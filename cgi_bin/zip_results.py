#!/usr/bin/env python

import cgi
import zipfile

from string import ascii_uppercase, digits
from os import path, listdir
from repeat_finder import read_configfile

config_filename = 'batchprimer.conf'
conf_arguments = read_configfile(config_filename)

html = ''

invalid_name_html = """\
Content-Type: text/html\n
<html><body>
<p>Invalid run name</p>
</body></html>
"""

no_input_html = """\
Content-Type: text/html\n
<html><body>
<p>No input or results file for this run name</p>
</body></html>
"""


if conf_arguments == '':
	html += 'Configuration file could not be read<br>'
else:
	data_dir = conf_arguments['DATADIR']

form = cgi.FieldStorage()

run_name = form['run'].value

#prevent download attacks
if len(run_name) != 6:
	html = invalid_name_html
elif not all(c in (ascii_uppercase + digits) for c in run_name):
	html = invalid_name_html
#seems like a legit run name, start zip creation
else:
	filelist = listdir(conf_arguments['DATADIR'])
	zip_files = []
	for filename in filelist:
		if filename.startswith(run_name):
			zip_files.append(filename)
	if len(zip_files) == 0:
		html = no_input_html
	else:
		zip_filename = conf_arguments['DATADIR'] + 'Batchprimer_' + run_name + '.zip'
		if not path.isfile(zip_filename):
			zip = zipfile.ZipFile(zip_filename, 'a')
			for zip_file in zip_files:
				zip.write(conf_arguments['DATADIR'] + zip_file, zip_file)
			zip.close()
		html = 'Content-Type:application/octet-stream\n'
		html += 'Content-Disposition: attachment; filename="'
		html += run_name + '.zip" ' + '\n\n'
		zip_file = open(zip_filename, 'rb')
		while True:
			buffer = zip_file.read(4096)
			if buffer:
				html += buffer
			else:
				break
		zip_file.close()

print html

