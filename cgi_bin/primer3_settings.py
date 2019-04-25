#!/usr/bin/env python

import sys


def main(args):
    # creates an HTML input form for primer3 files

    if len(args) == 1:
        primer3_settings_filename = 'primer3_settingsDavid.txt'
    else:
        primer3_settings_filename = args[1]

    with open(primer3_settings_filename, 'r') as primer3_settings_file:
        primer3_settings = primer3_settings_file.read()

    html = 'Content-type:text/html; charset=utf-8\n\n'

    html += '<html><head> <link rel="stylesheet" type="text/css" href="../html/primer3_settings.css" /> </head><body>'
    html += '<div class="container"><form>'
    for line in primer3_settings.split('\n'):
        if '=' in line and (line.startswith('PRIMER_') or line.startswith('P3_FILE_ID')):
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
            html += '\n'

    html += '<hr>'
    html += '<input type="submit" value="Download Primer3 parameters" name="Primer3settings" formaction="../cgi-bin/save_primer3settings.py" />'
    html += '</form></div>'
    html += '</body>'
    html += '</html>'

    sys.stdout.write(html)
    sys.stdout.flush()


if __name__ == '__main__':
    main(sys.args)
