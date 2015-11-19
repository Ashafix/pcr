#!/usr/bin/env python
import cgi, os
import cgitb; cgitb.enable()

message = ''
form_primerpairs = 25
form_maxsimilarity = 1
form_nested = True

form = cgi.FieldStorage()

# A nested FieldStorage instance holds the file
try:
	fileitem = form['fastafile']
except:
	fileitem = ''

# Test if the file was uploaded



# Test if the file was uploaded
if "Submit job" in form:
    if fileitem.filename:
        # strip leading path from file name to avoid directory traversal attacks
        fn = os.path.basename(fileitem.filename)
        message = 'The file "' + fn + '" was uploaded successfully'
    else:
        message = 'No file was uploaded'
        message += form.getvalue('maxrepeats') + '\n'
        message += form.getvalue('primerpairs') + '\n'
        message += form.getvalue('maxsimilarity') + '\n'
        message += form.getvalue('nested') + '\n'
        
elif "Test server status" in form:
    message = "test"
   
print """\
Content-Type: text/html\n
<html><body>
<form enctype="multipart/form-data" action="../cgi-bin/save_file.py" method="post">
<p>Primer3 parameter file: <input type="file" name="primer3file"></p>
<p>Sequence File: <input type="file" name="fastafile"></p>
<p>Target Sequence(s): <textarea name="fastasequence"></textarea></p>
<p>Maximum length of repeats which are searched: <input type="number" name="maxrepeats" value="3"></p>
<p>Maximum number of primers to be returned: <input type="number" name="primerpairs"
"""
print 'value="%s"' % (form_primerpairs)
print """" min="1" max="100" step="1"></p>
<p>Maximum similarity of primer pairs: <input type="number" name="maxsimilarity" 
"""
print 'value="%s"' % (form_maxsimilarity)
print """ min="0" max="1" step="0.1"></p>
<p>Search for nested primers: <input type="checkbox" name="nested" 
"""
if form_nested == True:
	print 'checked="checked">'
else:
	print '>'
print """
<p><input type="submit" value="Submit job" name="Submit job"></p>
<p><input type="submit" value="Test server status" name="Test server status"></p>
</form>
</body></html>
"""
