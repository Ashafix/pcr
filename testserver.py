#!/usr/bin/env python

#Tests if all the components of BatchPrimerDesign are working
from subprocess import check_output, STDOUT
from os import path
from repeat_finder import read_configfile

def test_server(gfServer, servername, serverport):

	command_line = str(gfServer) + ' status ' + str(servername) + ' ' + str(serverport)
	try:
		gfServer_response = check_output([command_line], shell = True, stderr = STDOUT)
	except:
		return False

	if gfServer_response.startswith('Couldn'):
		return False
	elif gfServer_response.find('version') >= 0 and \
		gfServer_response.find('port') >= 0 and \
		gfServer_response.find('host') >= 0 and \
		gfServer_response.find('type') >= 0:
		return True
	else:
		return False

conf_arguments = read_configfile()

message = ''
message += 'Configuration file could '
if conf_arguments == '':
	message += 'NOT be read<br>'
	message += 'NO further testing was possible to due a missing .conf file'
else:
	message += 'be read<br><br>'
	message += str(conf_arguments) + '<br><br>'

if conf_arguments != '':
	message += 'gfServer is '
	if test_server(conf_arguments['GFSERVER'], conf_arguments['SERVERNAME'], conf_arguments['SERVERPORT']):
		message += 'up and running<br>'
	else:
		message += 'IS NOT running<br>'
	message += 'Primer3 executable'
	if path.isfile(conf_arguments['PRIMER3_EXE']):
		message += ' is found<br>'
	else:
		message += ' IS NOT found<br>'

message += '<form action="../primer.html">    <input type="submit" value="Go back to start page"></form>'


print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)
