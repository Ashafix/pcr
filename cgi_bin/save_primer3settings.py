#!/usr/bin/env python

#creates an primer3 setting file from a cgi form

import sys
import cgi

html = 'Content-Type:application/octet-stream\n'
html += 'Content-Disposition: attachment; '
html += 'filename="primer3settings.ini"\n\n'

if len(sys.argv) == 1:
	primer3_settings_filename = 'primer3_v1_1_4_default_settings.txt'
else:
	primer3_settings_filename = sys.argv[1]
with open(primer3_settings_filename, 'r') as primer3_settings_file:
		primer3_settings = primer3_settings_file.read()

form = cgi.FieldStorage()

html += 'Primer3 File - http://primer3.sourceforge.net\n'
html += 'P3_FILE_TYPE=settings\n'

for line in primer3_settings.split('\n'):
	if '=' in line and (line.startswith('PRIMER_') or line.startswith('P3_FILE_ID')):
		cells = line.split('=')
		if len(cells) == 3:
			if cells[0] in form.keys:
				html += str(key)
				html += '='
				html += str(form[key].value)
				html += '\n'
html += '=\n'

print (html)
