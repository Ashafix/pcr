#!/usr/bin/env python

#creates an HTML input form for primer3 files

import sys

if len(sys.argv) == 1:
	primer3_settings_filename = 'primer3_v1_1_4_default_settings.txt'
	with open(primer3_settings_filename, 'r') as primer3_settings_file:
		primer3_settings = primer3_settings_file.read()
else:
	primer3_settings_filename = sys.argv[1]

html = 'Content-type:text/html; charset=utf-8\n\n'
html += '<html><body>'

for line in primer3_settings.split('\n'):
	if '=' in line and line.startswith('PRIMER_'):
		html += '<li>'
		html += '<label>'
		html += line.split('=')[0]
		html += '</label>'
		html += '<input name="'
		html += line.split('=')[0]
		html += '"'
		html += ' value="'
		html += line.split('=')[1].strip()
		html += '"'
		html += ' />'
		html += '</li>'
	elif len(line.strip()) > 1:
		html += '<br>\n'
	
html += '<hr>'

html += '<input type="submit" value="Change Primer3 parameters" name="Primer3settings" formaction="../cgi-bin/save_primer3settings.py" />'
html += '<a href="../cgi-bin/save_primer3settings.py"><img src="/images/Farm-Fresh_file_extension_zip.png"</a>'
html += '<a href="../cgi-bin/load_primer3settings.py">Upload</a>'

html += '</body>'
html += '</html>'


sys.stdout.write(html)
sys.stdout.flush()


