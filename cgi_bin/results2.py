#!/usr/bin/env python

import cgi

results = """
==========
Target:, CA1 hg19_microsat_21xCA range=chr2:36894133-36894974 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, TG1 hg19_microsat_30xTG range=chr2:36944078-36944938 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, ATTCTCCTGCCTCAGCCTGGGACTA, GAAACCCTGTCTCACACGGTGAAAC
Amplicon:, chr2:36944426+36944577, 152bp, ATTCTCCTGCCTCAGCCTGGGACTAcaggctcccaccaccacgcctggctaatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtttagtagagatgggGTTTCACCGTGTGAGACAGGGTTTC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
66.69, 64.12, 56.00, 52.00, 86.36, 53.29
Primer pair:, GGCACAATCTTGGCTCACTGCAAG, GAAACCCTGTCTCACACGGTGAAAC
Amplicon:, chr2:36944380+36944577, 198bp, GGCACAATCTTGGCTCACTGCAAGcaggctcccaccaccacgcctggctaatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtttagtagagatgggGTTTCACCGTGTGAGACAGGGTTTC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
64.91, 64.12, 54.17, 52.00, 88.21, 52.98
==========
Target:, AC1 hg19_microsat_22xAC range=chr2:37063707-37064551 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, ACCCACTTGGAAGAAATTTAGTTGG, ATTAAGAAGGTTTCCATTCCTGGGT
Amplicon:, chr2:37064068+37064257, 190bp, ACCCACTTGGAAGAAATTTAGTTGGactgtttgcattctacacacacacacacacacacacacacacacacacacacacacacaaatggagtaaagacataaatgtagaaaaccaaaaccaaaaaacaaaaaatgtagaagccattctagcggcctatacatgccACCCAGGAATGGAAACCTTCTTAAT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.70, 60.22, 40.00, 40.00, 81.49, 39.47
Primer pair:, TGTTTAATAGAGTGCTACACTGGCA, ATTAAGAAGGTTTCCATTCCTGGGT
Amplicon:, chr2:37064043+37064257, 215bp, TGTTTAATAGAGTGCTACACTGGCAactgtttgcattctacacacacacacacacacacacacacacacacacacacacacacaaatggagtaaagacataaatgtagaaaaccaaaaccaaaaaacaaaaaatgtagaagccattctagcggcctatacatgccACCCAGGAATGGAAACCTTCTTAAT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.28, 60.22, 40.00, 40.00, 81.88, 39.47
==========
Target:, AC2 hg19_microsat_22xAC range=chr2:37113786-37114629 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, TGCAATTTCCTAGAATCAGTTTCTCC, GCCGAGAAGTTCTTGATTGTAAAGT
Amplicon:, chr2:37114154+37114292, 139bp, TGCAATTTCCTAGAATCAGTTTCTCCtgaaagacacacacacacacacacacacacacacacacacacacacacacggaagattttagtgatttttagtaaattaagcacaaacACTTTACAATCAAGAACTTCTCGGC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.62, 59.82, 38.46, 40.00, 80.07, 38.85
Primer pair:, TCACTAAGAAGAAATGATCAGTGCA, GCCGAGAAGTTCTTGATTGTAAAGT
Amplicon:, chr2:37114133+37114292, 160bp, TCACTAAGAAGAAATGATCAGTGCAtgaaagacacacacacacacacacacacacacacacacacacacacacacggaagattttagtgatttttagtaaattaagcacaaacACTTTACAATCAAGAACTTCTCGGC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
58.53, 59.82, 36.00, 40.00, 80.34, 38.41
==========
Target:, AT1 hg19_microsat_20xAT range=chr2:37141976-37142816 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, CTGCACTCCAGGCTGGGTGACAGAG, ACTGAAATACGTACCTTGTGCTAGA
Amplicon:, chr2:37142301+37142446, 146bp, CTGCACTCCAGGCTGGGTGACAGAGcaagactccgtctcaaaaaaaaaaaaaggaaatttaaactgaatacataaatatatatatatatatatatatatatatatatatatatataaagccTCTAGCACAAGGTACGTATTTCAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
68.70, 59.82, 64.00, 40.00, 76.14, 28.77
Primer pair:, GTGGAGCTTGCAGTGAGCCGAGATC, ACTGAAATACGTACCTTGTGCTAGA
Amplicon:, chr2:37142270+37142446, 177bp, GTGGAGCTTGCAGTGAGCCGAGATCcaagactccgtctcaaaaaaaaaaaaaggaaatttaaactgaatacataaatatatatatatatatatatatatatatatatatatatataaagccTCTAGCACAAGGTACGTATTTCAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
67.48, 59.82, 60.00, 40.00, 79.20, 28.08
==========
Target:, AC3 hg19_microsat_24xAC range=chr2:37209607-37210454 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, AATTGCACAAAGATACATGTCTACA, CACAGACAATAAACACTTCTCGTCC
Amplicon:, chr2:37209966+37210086, 121bp, AATTGCACAAAGATACATGTCTACAtataacagacacagatacacacacacacacacacacacacacacacacacacacacacacacacgtataggGGACGAGAAGTGTTTATTGTCTGTG
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
57.31, 60.11, 32.00, 44.00, 80.78, 42.15
Primer pair:, AGCTCCTATCAATTCCTGCATCTAA, CACAGACAATAAACACTTCTCGTCC
Amplicon:, chr2:37209888+37210086, 199bp, AGCTCCTATCAATTCCTGCATCTAAtataacagacacagatacacacacacacacacacacacacacacacacacacacacacacacacgtataggGGACGAGAAGTGTTTATTGTCTGTG
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.69, 60.11, 40.00, 44.00, 80.48, 43.8
==========
Target:, TG2 hg19_microsat_20xTG range=chr2:37286150-37286990 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, GGAAATTCAGAGGACTATGATCCCA, ATTGAGTCAGGAGAATTGCTTGAAC
Amplicon:, chr2:37286376+37286726, 351bp, GGAAATTCAGAGGACTATGATCCCAtaggaattcagatgactacaaagaaagaaattttaaggcattgtttatacacatatacatttatgtgtataaacaatgccttaaaatttacatgaaatttttacatatattaaatatatttttgcaacttttacagatatatatgtatatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtatatatatatatatatatttttttttttttttttttgagagagtctcactctgtcaaccaggctggagtgcagtggcggaatctcggctcactgcaacctccacgtcctagGTTCAAGCAATTCTCCTGACTCAAT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.93, 59.82, 44.00, 40.00, 80.30, 33.05
Primer pair:, ACATTTATGTGTATAAACAATGCCT, ATTGAGTCAGGAGAATTGCTTGAAC
Amplicon:, chr2:37286457+37286726, 270bp, ACATTTATGTGTATAAACAATGCCTtaggaattcagatgactacaaagaaagaaattttaaggcattgtttatacacatatacatttatgtgtataaacaatgccttaaaatttacatgaaatttttacatatattaaatatatttttgcaacttttacagatatatatgtatatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtatatatatatatatatatttttttttttttttttttgagagagtctcactctgtcaaccaggctggagtgcagtggcggaatctcggctcactgcaacctccacgtcctagGTTCAAGCAATTCTCCTGACTCAAT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
55.59, 59.82, 28.00, 40.00, 79.90, 31.91
==========
Target:, AC4 hg19_microsat_22xAC range=chr2:37476302-37477146 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, CTGAGGTAGGATAATCGCTTGAACC, GTGTCTCTATCACAGGCTACAGTG
Amplicon:, chr2:37476619+37476790, 172bp, CTGAGGTAGGATAATCGCTTGAACCcgggaggcggaggttgcagtgaggggagattgctccgttgcactctagcctgtgatagacacacacacacacacacacacacacacacacacacacacacacagaggggagatcgctccgttgCACTGTAGCCTGTGATAGAGACAC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
61.02, 60.44, 48.00, 50.00, 87.38, 54.65
Primer pair:, CTGTAATCCTAGCTACTCACGAGG, GTGTCTCTATCACAGGCTACAGTG
Amplicon:, chr2:37476595+37476790, 196bp, CTGTAATCCTAGCTACTCACGAGGcgggaggcggaggttgcagtgaggggagattgctccgttgcactctagcctgtgatagacacacacacacacacacacacacacacacacacacacacacacagaggggagatcgctccgttgCACTGTAGCCTGTGATAGAGACAC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.78, 60.44, 50.00, 50.00, 87.57, 54.97
==========
Target:, AC5 hg19_microsat_24xAC range=chr2:37526255-37527103 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, CTAGCCTGGTCAACATGGTGAAAC, TCTGTAGGTTGTCACTTCACTTGTT
Amplicon:, chr2:37526614+37526749, 136bp, CTAGCCTGGTCAACATGGTGAAACcccacctctactaaaatacacacacacacacacacacacacacacacacacacacacacacacacaagcttctgcaaggaaataattAACAAGTGAAGTGACAACCTACAGA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
61.87, 60.34, 50.00, 40.00, 82.14, 44.12
Primer pair:, ACTCACACTGATAATCCTAGCACTC, TCTGTAGGTTGTCACTTCACTTGTT
Amplicon:, chr2:37526545+37526749, 205bp, ACTCACACTGATAATCCTAGCACTCcccacctctactaaaatacacacacacacacacacacacacacacacacacacacacacacacacaagcttctgcaaggaaataattAACAAGTGAAGTGACAACCTACAGA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
59.93, 60.34, 44.00, 40.00, 84.93, 43.07
==========
Target:, AC6 hg19_microsat_24xAC range=chr2:37623113-37623960 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, AC7 hg19_microsat_22xAC range=chr2:37830003-37830846 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, AC8 hg19_microsat_23xAC range=chr2:38099690-38100536 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, CTTTCATTCTTTCCACTTGCTCTCC, TGGAAAGTGTCTGAAGTGTCTGAA
Amplicon:, chr2:38100051+38100160, 110bp, CTTTCATTCTTTCCACTTGCTCTCCtcccaaccctacagacacacacacacacacacacacacacacacacacacacacacacacaTTCAGACACTTCAGACACTTTCCA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.34, 60.08, 44.00, 41.67, 82.39, 47.27
Primer pair:, CTACCTAGCCTGGCAAGCTTTCATT, TGGAAAGTGTCTGAAGTGTCTGAA
Amplicon:, chr2:38100034+38100160, 127bp, CTACCTAGCCTGGCAAGCTTTCATTtcccaaccctacagacacacacacacacacacacacacacacacacacacacacacacacaTTCAGACACTTCAGACACTTTCCA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
63.12, 60.08, 48.00, 41.67, 83.75, 48.18
==========
Target:, AC9 hg19_microsat_23xAC range=chr2:38265791-38266637 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, GATTTGAGCTTTGCAAGTGACAATG, AAGGACAATCCCAAGTGACTAAATT
Amplicon:, chr2:38266124+38266361, 238bp, GATTTGAGCTTTGCAAGTGACAATGaaaataatatttttgagcaacagtttaaaagccagatgctatacacacacacacacacacacacacacacacacacacacacacacacagagagagagataaaatgttcatggattaagattatatattcatataattttaactatattcatatggattaaaactaatccatatgattatggtaaaatAATTTAGTCACTTGGGATTGTCCTT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.11, 58.69, 40.00, 36.00, 78.69, 31.09
Primer pair:, CTGGTGGTTCCCATAGAGGTGTAC, AAGGACAATCCCAAGTGACTAAATT
Amplicon:, chr2:38266054+38266361, 308bp, CTGGTGGTTCCCATAGAGGTGTACaaaataatatttttgagcaacagtttaaaagccagatgctatacacacacacacacacacacacacacacacacacacacacacacacagagagagagataaaatgttcatggattaagattatatattcatataattttaactatattcatatggattaaaactaatccatatgattatggtaaaatAATTTAGTCACTTGGGATTGTCCTT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
62.20, 58.69, 54.17, 36.00, 81.55, 32.49
==========
Target:, TG3 hg19_microsat_20xTG range=chr2:38321641-38322480 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, AC10 hg19_microsat_21xAC range=chr2:38656070-38656911 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, TG4 hg19_microsat_23xTG range=chr2:38902286-38903131 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, GT1 hg19_microsat_20xGT range=chr2:38944049-38944888 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, TACCTGGTCTCTGTATTAAGGGAGT, TATTAGCACTTACCTGGCACATAGT
Amplicon:, chr2:38944426+38944539, 114bp, TACCTGGTCTCTGTATTAAGGGAGTgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtataaaagagagtgagagagtacacacACTATGTGCCAGGTAAGTGCTAATA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.04, 59.63, 44.00, 40.00, 81.18, 43.86
Primer pair:, AGTTTATGCTGTGATTAATACCTGGT, TATTAGCACTTACCTGGCACATAGT
Amplicon:, chr2:38944408+38944539, 132bp, AGTTTATGCTGTGATTAATACCTGGTgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtataaaagagagtgagagagtacacacACTATGTGCCAGGTAAGTGCTAATA
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
58.65, 59.63, 34.62, 40.00, 81.00, 41.74
==========
Target:, TA1 hg19_microsat_20xTA range=chr2:39393556-39394395 5'pad=400 3'pad=400 strand=+ repeatMasking=none

==========
Target:, TG5 hg19_microsat_26xTG range=chr2:39913704-39914556 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, TACGTCATCATGCTGCTTGACATAA, ACTTTACTACCCTACTCACTGCATC
Amplicon:, chr2:39914006+39914188, 183bp, TACGTCATCATGCTGCTTGAC
ATAAaattagggctggaaatgttttgggggcctgagatgtaggctaaaatgtggcagagtatatgtgcacatatgcatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtattatgaGATGCAGTGAGTAGGGTAGTAAAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.91, 59.87, 40.00, 44.00, 83.10, 43.72
Primer pair:, AGCTGATTTAAGGGATGCTTAGGAA, ACTTTACTACCCTACTCACTGCATC
Amplicon:, chr2:39913941+39914188, 248bp, AGCTGATTTAAGGGATGCTTAGGAAaattagggctggaaatgttttgggggcctgagatgtaggctaaaatgtggcagagtatatgtgcacatatgcatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtattatgaGATGCAGTGAGTAGGGTAGTAAAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
60.10, 59.87, 40.00, 44.00, 84.56, 43.72
==========
Target:, TA2 hg19_microsat_21xTA range=chr2:40046738-40047580 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, GTGACAAGAACGAGACTCCAACTC, ACTTCATTCTATAGCGTTTGTGTCT
Amplicon:, chr2:40047089+40047226, 138bp, GTGACAAGAACGAGACTCCAACTCaaaaaaaaaaaaatgtgtgtgtgtgtatatatatatatatatatatatatatatatatatatatatatttacattgtttaaaatttataAGACACAAACGCTATAGAATGAAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
61.32, 58.60, 50.00, 36.00, 72.73, 21.01
Primer pair:, CGAGATCACGTCATTGCCCTTCAG, ACTTCATTCTATAGCGTTTGTGTCT
Amplicon:, chr2:40047060+40047226, 167bp, CGAGATCACGTCATTGCCCTTCAGaaaaaaaaaaaaatgtgtgtgtgtgtatatatatatatatatatatatatatatatatatatatatatttacattgtttaaaatttataAGACACAAACGCTATAGAATGAAGT
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
63.77, 58.60, 54.17, 36.00, 76.16, 21.74
"""

html = 'Content-Type: text/html\n\n<html><head> <link rel="stylesheet" type="text/css" href="results.css" /> </head><body>'

if 'result' in cgi.FieldStorage().keys():
	result_filename = '/var/www/data/'
	result_filename += cgi.FieldStorage()['result'].value
	result_filename += '_results.txt'
	try:
		result_file = open(result_filename, 'r')
		results = result_file.read()
		result_file.close()
	except:
		results = ''
		html += '<br>No results were found<br>'
else:
	html += '<h1>THIS IS ONLY TEST DATA</h1><br>'


class Primer:
	def __init__(self):
		self.forward = ''
		self.reverse = ''
		self.TMf = -1
		self.TMr = -1
		self.GCf = -1
		self.GCr = -1
		self.TMproduct = -1
		self.GCproduct = -1

class Amplicon:
	def __init__(self):
		self.product = ''
		self.location = ''
		self.size = ''

def parse_output(output_text):
	target = ''
	new_primer = Primer()
	new_amplicon = Amplicon()
	primers = []
	amplicons = []
	
	primer_table = False
	
	lines = output_text.split('\n')
	for line in lines:
		if line.startswith('Target:'):
			if len(line.split(',')) > 0:
				target = line.split(',')[1].strip()
				new_primer = Primer()
				new_amplicon = Amplicon()
			primer_table = False
		elif line.startswith('Primer pair:'):
			new_primer = Primer()
			new_primer.forward = line.split(',')[1].strip()
			new_primer.reverse = line.split(',')[2].strip()
			primer_table = False
		elif line.startswith('Amplicon:'):
			new_amplicon = Amplicon()
			new_amplicon.location = line.split(',')[1].strip()
			new_amplicon.size = line.split(',')[2].strip()
			new_amplicon.product = line.split(',')[3].strip()
			primer_table = False
		elif line.startswith('primerF TM'):
			primer_table = True
		elif primer_table == True:
			primer_properties = line.split(',')
			if len(primer_properties) == 6:
				new_primer.TMf = primer_properties[0].strip()
				new_primer.TMr = primer_properties[1].strip()
				new_primer.GCf = primer_properties[2].strip()
				new_primer.GCr = primer_properties[3].strip()
				new_primer.TMproduct = primer_properties[4].strip()
				new_primer.GCproduct = primer_properties[5].strip()
				if target != '' and new_amplicon.product != '' and new_primer.forward != '':
					amplicons.append(new_amplicon)
					primers.append(new_primer)
			primer_table = False
	return target, amplicons, primers

def result_to_html(result):
	target, amplicons, primers = parse_output(result)
	html = '<p class="target"><b>Target: </b>'
	html += target
	html += '<br><br>'
	html += '<table class="resulttable">'
	if len(primers) > 0:
		html += '<tr><th colspan="3">Forward Primer</th><th colspan="3">Reverse Primer</th><th class="amplicon" colspan="5">Amplicon</th></th></tr>'
		#html += '</table><table class="resulttable">'
		html += '<tr><th class="primer">Sequence</th><th class="digits4">TM</th><th class="digits4">GC</th><th class="primer">Sequence</th><th class="digits4">TM</th><th class="digits4">GC</th><th>Sequence</th><th class="location">Location</th><th class="size">Size</th><th class="digits4">TM</th><th class="digits4">GC</th>'
	else:
		html += '<font color="red">No suitable primer pairs found</font>'
	i = -1
	for primer_pair in primers:
		i += 1
		html += '<tr>'
		html += '<td class="sequence">'
		html += primer_pair.forward
		html += '</td>'
		html += '<td >'
		html += primer_pair.TMf
		html += '</td>'
		html += '<td >'
		html += primer_pair.GCf
		html += '</td>'
		html += '<td class="sequence">'
		html += primer_pair.reverse
		html += '</td>'
		html += '<td >'
		html += primer_pair.TMr
		html += '</td>'
		html += '<td >'
		html += primer_pair.GCr
		html += '</td>'
		html += '<td class="amplicon">'
		html += amplicons[i].product
		html += '</td>'
		html += '<td>'
		html += '<a href="http://genome.ucsc.edu/cgi-bin/hgTracks?org=Human&db=hg19&position='
		html += amplicons[i].location.replace('+', '-')
		html += '">' + amplicons[i].location +'</a>'
		html += '</td>'
		html += '<td>'
		html += amplicons[i].size.replace('bp', '')
		html += '</td>'
		html += '<td >'
		html += primer_pair.TMproduct
		html += '</td>'
		html += '<td >'
		html += primer_pair.GCproduct
		html += '</td>'
	html += '</table>'
	html += '</p>'
	html += '<hr>'
	return html



result = ''
for line in results.split('\n'):
	if line.startswith('Target:'):
		if result != '':
			#print result
			html += result_to_html(result)
		result = line + '\n'
	else:
		if line != '==========' and line.strip() != '':
			result += line + '\n'

html += result_to_html(result)
html += '</body></html>'

print html


x,y,z= parse_output("""Target:, TG1 hg19_microsat_30xTG range=chr2:36944078-36944938 5'pad=400 3'pad=400 strand=+ repeatMasking=none

Primer pair:, ATTCTCCTGCCTCAGCCTGGGACTA, GAAACCCTGTCTCACACGGTGAAAC
Amplicon:, chr2:36944426+36944577, 152bp, ATTCTCCTGCCTCAGCCTGGGACTAcaggctcccaccaccacgcctggctaatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtttagtagagatgggGTTTCACCGTGTGAGACAGGGTTTC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
66.69, 64.12, 56.00, 52.00, 86.36, 53.29
Primer pair:, GGCACAATCTTGGCTCACTGCAAG, GAAACCCTGTCTCACACGGTGAAAC
Amplicon:, chr2:36944380+36944577, 198bp, GGCACAATCTTGGCTCACTGCAAGcaggctcccaccaccacgcctggctaatgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtttagtagagatgggGTTTCACCGTGTGAGACAGGGTTTC
primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC
64.91, 64.12, 54.17, 52.00, 88.21, 52.98""")

