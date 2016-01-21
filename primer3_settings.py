


#create an HTML input form for primer3 files


primer3_settings = open('primer3_v1_1_4_default_settings.txt', 'r')


print '<html><body>'

for line in primer3_settings.readlines():
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
		print html
	elif len(line.strip()) > 1:
		print line
		print '<br>'
primer3_settings.close()

print '</body>'
print '</html>'