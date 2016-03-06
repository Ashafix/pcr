#!/usr/bin/env python

#creates an primer3 setting file from a cgi form

import sys
import cgi

html = 'Content-Type:application/octet-stream\n'
html += 'Content-Disposition: attachment; '
html += 'filename="primer3settings.ini"\n\n'

form = cgi.FieldStorage()
for key in form.keys()  :
	html += str(key)
	html += '='
	html += str(form[key].value)

print (html)
