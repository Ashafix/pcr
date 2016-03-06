#!/usr/bin/env python

#creates an HTML input form for primer3 files

import sys

if len(sys.argv) == 1:
	primer3_settings_filename = 'primer3_v1_1_4_default_settings.txt'
	with open(primer3_settings_filename, 'r') as primer3_settings_file:
		primer3_settings = primer3_settings_file.read()
else:
	primer3_settings_filename = sys.argv[1]

print ('Content-Type: text/html')
print ('<html><body>')

for line in primer3_settings.split('\n'):
	if '=' in line and line.startswith('PRIMER_'):
		html = ''
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
		html += '>'
		html += '</li>'
		print (html)
	elif len(line.strip()) > 1:
		print (line)
		print ('<br>')

print ('<hr>')

print ('<input type="submit" value="Save Primer3 parameters to file" name="SaveSettings" formaction="cgi-bin/save_primer3settings.py" />')
print ('<input type="submit" value="Load Primer3 parameters from file" name="SaveSettings" formaction="cgi-bin/load_primer3settings.py" />')
print ('</body>')
print ('</html>')
