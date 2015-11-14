import sys
import os
from subprocess import Popen, PIPE
import subprocess
from multiprocessing import Pool

print ''

nucleotides = ['A', 'T', 'C', 'G']
ssr_list = ['AAAATTC', 'ATCCCCCCCG', 'AAAATTG', 'ATCCCCCCCC', 'AAATCCCGGGGG', 'AGG', 'ATTCCCCC', 'AAAATTT', 'AATTTTTTCCCC', 'AATTTTTTCCCG', 'TTTTGGG', 'AAACCCCCGGG', 'AAAAATTTGGGG', 'ATTCCCCCCCGG', 'AAAACCCCGGGG', 'ATTCCCCG', 'AAACCCGGG', 'AATCCCGGGGGG', 'AAAACCCGGG', 'AAAATTCCG', 'ATTCCCCGG', 'ATTTCCCCCGGG', 'GG', 'AATTCGGGGGGG', 'ATTTTCCCCGGG', 'TTTCCGGGGGG', 'TTTTTTTGGGG', 'AATCGGGGG', 'TTTGGGGGGG', 'AAAAAAAACGGG', 'CCGGGG', 'TTTTTTCCCCC', 'ATTCCG', 'AATTTCCGGGGG', 'ATTCCC', 'TTTTTTTCCCCC', 'AAAAAAACGGGG',...(line truncated)...
max_similarity = 0.5
pcr_location = './'

#prints help
def print_help():
	print 'Usage'
	print '-FASTA %filename : Specifies filename of fasta for which repeats and appropriate primers will be searched, e.g. -FASTA BRCA_markers.fa'
	print '-PRIMER3_SETTINGS %filename : Specifies filename which specifies the settings which are used for searching primers, e.g. -PRIMER3_SETTINGS BRCA_markers_primers.txt'
	print '-PRIMER3_DIRECTOY %directory : Specifies a directory where the output files will be saved, e.g. PRIMER3_DIRECTORY c:/pcr/BRCA_markers/'
	print '-PRIMER3_EXE %filename : Specifies the location of the primer3_core.exe, e.g. -PRIMER3_EXE primer3_core.exe'
	print '-SERVERNAME name : Specifies the name of the isPCR server {usually name of the computername), e.g. -SERVERNAME pcrcomputer'
	print '-SERVERPORT number : Specifies the port which is used to communicate with the isPCR server, e.g. -SERVERPORT 33334'
	print '-MAXREPEATS number : Specifies the maximum length of repeats to search, e.g. -MAXREPEATS 3, searches for repeats of di- and trinucleotides'
	print '-PRIMERPAIRS number : Specifies the number of suitable primer pairs which will be returned'
	print '-GFSERVER filename : Specifies the location of the gfServer.exe'
	print '-GFPCR filename : Specifies the location of the gfPCR.exe'
	print '-MAX_SIMILARITY number : Specifies the maximal similarity for two primer pairs in order to be accepted, from 0 to 1, default = 0.5' #not included yet
	print '@filename : Specifies a file which list the above mentioned arguments, arguments used with -ARGUMENT will overwrite the arguments in the file, NOT IN USE YET'
	print '-NESTED : Specifies whether the program should search for nested primers if not enough pairs have been found (0), never search (-1) or always search for primers (1)'
	print '-OUTPUT filename : Specifies the output filename where all the primers and target will be saved, default: batchprimer_output.txt'
	print '-MAXTHREADS number : Specifies how many threads are started in parallel, should be less than your number of CPU cores'
	print '-REMOVETEMPFILES boolean : Specifies whether temporary files (e.g. Primer3 input and output) will be deleted after the program finishes. Default is FALSE'
	return True

#tests the gfServer and returns True if the server is working
def test_server(gfServer, servername, serverport):

	process = Popen([gfServer,'status', servername, str(serverport)], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
	x = process.communicate()[0]
	if x.startswith('Couldn'):
		return False
	elif x.find('version') >= 0 and x.find('port') >= 0 and x.find('host') >= 0 and x.find('type') >= 0:
		return True
	else:
		return False

#takes a list of isPCRoutputs and counts the numbers of amplicons for a primer pair
def count_amplicons(isPCRoutput, primerF, primerR):
	if not isPCRoutput.find(primerF) >= 0 and not isPCRoutput.find(primerR) >= 0:
		return -1
	else:
		startpoint = isPCRoutput.find(primerF + ';' + primerR)
		isPCRfragment = isPCRoutput[startpoint:]
		if isPCRfragment.find(';', len(primerF) + len(primerR) + 2) >= 0:
			isPCRfragment = isPCRfragment[0:isPCRfragment.find(';', len(primerF) + len(primerR) + 2)]
			return isPCRfragment.count('>')
		else:
			return isPCRfragment.count('>')

#creates a list of sequences which should be excluded from primer binding sites
def exclude_list(sequence):
	to_exclude = []
	for ssr in ssr_list:
		if len(ssr) <= 3:
			max_length = 0
			for i in xrange(1, len(sequence) / 2):
				if sequence.find(ssr * i) >= 0 and i * len(ssr) >= 9:
					max_length = i
			if max_length > 0:
				to_exclude.append(ssr * max_length)

	return to_exclude


#imports filenames from commandline
def import_parameters():
	global fasta_filename
	global standard_primer_settings_filename
	global primer3_directory
	global primer3_exe
	global servername
	global serverport
	global gfServer
	global gfPCR
	global max_repeats
	global max_primerpairs
	global nested
	global output_filename
	global max_threads
	global remove_temp_files

	if len(sys.argv) > 1:
		if str(sys.argv).find('-help') > -1:
			print_help()
			exit()

		for i in xrange(len(sys.argv)):
			if str(sys.argv[i]).upper() == '-FASTA':
				fasta_filename = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-PRIMER3_SETTINGS' or \
				str(sys.argv[i]).upper() == '-PRIMER_SETTINGS':
				standard_primer_settings_filename = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-PRIMER3_DIRECTORY' or \
				str(sys.argv[i]).upper() == '-PRIMER_DIRECTORY':
				primer3_directory = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-PRIMER3_EXE':
				primer3_exe = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-SERVERNAME':
				servername = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-SERVERPORT':
				serverport = int(sys.argv[i + 1])
			elif str(sys.argv[i]).upper() == '-MAXREPEATS':
				max_repeats = int(sys.argv[i + 1])
			elif str(sys.argv[i]).upper() == '-PRIMERPAIRS':
				max_primerpairs = int(sys.argv[i + 1])
			elif str(sys.argv[i]).upper()=='-GFSERVER':
				gfServer = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-GFPCR':
				gfPCR = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-NESTED':
				nested = int(sys.argv[i + 1])
			elif str(sys.argv[i]).upper() == '-OUTPUT':
				output_filename = sys.argv[i + 1]
			elif str(sys.argv[i]).upper() == '-MAXTHREADS':
				max_threads = int(sys.argv[i + 1])
			elif str(sys.argv[i]).upper() == '-REMOVETEMPFILES':
				remove_temp_files = bool(sys.argv[i + 1])

	if fasta_filename == '' or \
		standard_primer_settings_filename == '' or \
		primer3_directory == '' or \
		primer3_exe == '' or \
		servername == '' or \
		serverport == -1 or \
		max_repeats == -1 or \
		gfServer == '' or \
		gfPCR == '' or \
		abs(nested) > 1:
		print fasta_filename
		print standard_primer_settings_filename
		print primer3_directory
		print primer3_exe
		print servername
		print serverport
		print gfServer
		print gfPCR
		print nested
		print 'Missing arguments!'
		print_help()
		exit()

	return True


#finds the longest repeat in a given sequence
def find_repeats(sequence, max_length):
	longest_repeat = ''

	for ssr in ssr_list:
		if len(ssr) <= int(max_length):
			i = 1
			while sequence.find(ssr * i) >= 0:
				i += 1
			i += -1
			if len(ssr * i) > len(longest_repeat):
				longest_repeat = ssr * i

	return longest_repeat

#finds the length of dinucleotide repeats, i.e. ACTAGAGAGTCA would return 6
def dinucleotide_repeat(sequence):
	nucleotides = 'ATGC'
	max_repeat = 0
	for i in xrange(4):
		for j in xrange(4):
			n = 1
			while sequence.find((nucleotides[i] + nucleotides[j]) * n) > -1:
				n += 1
			if n - 1 > max_repeat:
				max_repeat = n - 1

	return max_repeat * 2

#creates the input file for primer3
#if primerF and primerR are given, primerR is kept fixed and primerF is excluded, useful for nested PCR
def create_primer3_file(seq_name, sequence, target, exclude, primerF, primerR):
	if len(target) >= len(sequence) or sequence.find(target) < 0:
		return False
	new_filename = 'primer3_' + makefilename(seq_name)
	primer3_file = open(primer3_directory + new_filename + '.txt', 'w')

	primer3_file.write('SEQUENCE_ID=')
	primer3_file.write(seq_name + '\n')
	primer3_file.write('SEQUENCE_TEMPLATE=')
	primer3_file.write(sequence + '\n')
	primer3_file.write('SEQUENCE_TARGET=')
	primer3_file.write(str(sequence.find(target) + 1))
	primer3_file.write(',')
	primer3_file.write(str(len(target)) + '\n')
	primer3_file.write('SEQUENCE_EXCLUDED_REGION=')
	excluded_region = str(sequence.find(target) + 1) + ',' + str(len(target)) + '\n'
	if not exclude == None:
		for excluded_seq in exclude:
			excluded_region += 'SEQUENCE_EXCLUDED_REGION='
			excluded_region += str(sequence.find(excluded_seq) + 1) + ','
			excluded_region += str(len(excluded_seq)) + '\n'
	primer3_file.write(excluded_region)
	if primerF != '' and primerR != '':
		primer3_file.write('SEQUENCE_EXCLUDED_REGION=' + str(int(sequence.find(primerF) + len(primerF) / 3)) + ',' + str(int(len(primerF) / 3)) + '\n')
		primerR = primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
		primer3_file.write('SEQUENCE_FORCE_RIGHT_END=' + str(sequence.find(primerR)) + '\n')
		primer3_file.write('SEQUENCE_FORCE_RIGHT_START=' + str(sequence.find(primerR) + len(primerR) - 1) + '\n')

	standard_primer3_file = open(standard_primer_settings_filename, 'ru')
	for line in standard_primer3_file.readlines():
		primer3_file.write(line)

	standard_primer3_file.close()
	primer3_file.close()

	return True

#cleans a filename
def makefilename(old_name):
	old_name = old_name.replace(' ', '_')
	old_name = old_name.translate(None, '=!/\<>:"|?*\'')
	return old_name

#takes a primer pair, a input sequence for which the primers were designed and checks in the isPCRoutput if the target sequence is amplified or something else
#also checks if the number of amplicons is exactly one
def check_specificity(primerF, primerR, targetSequence, isPCRoutput):
	found = False
	isPCRamplicon = ''
	temp_output = isPCRoutput.splitlines(True)
	i = 0

	#checks if only one is amplicon created, if yes, continue, otherwise break the function
	if count_amplicons(isPCRoutput, primerF, primerR) != 1:
		return False

	while i < len(temp_output):
		line = temp_output[i]
		if found == False and isPCRamplicon == '':
			if line.find(' ' + primerF + ' ' + primerR + '\n') >= 0 and \
				line.startswith('>'):
				found = True
		elif found == True and (not line.startswith('>') and \
			line.find(';') == -1):
			isPCRamplicon += line
		elif line.startswith('>') or line.find(';') >= 0 and \
			found == True:
			i = len(temp_output)
		i += 1

	if isPCRamplicon == '':
		return False
	else:
		isPCRamplicon = isPCRamplicon.replace('\n', '')
		isPCRamplicon = isPCRamplicon[len(primerF):]
		isPCRamplicon = isPCRamplicon[0:len(isPCRamplicon) - len(primerR)]

		if targetSequence.upper().find(isPCRamplicon.upper()) >= 0:
			return True
		else:
			return False

#takes primer3output and returns the amplicon based on primerF and primerR bindingsites and input sequence
#returns the amplicon without the primers
def get_amplicon_from_primer3output(primerF, primerR, primer3output):

	amplicon_start = 0
	primerF_found = False
	sequence = ''
	end_line = 0
	orig_output = primer3output

	while amplicon_start == 0 and primer3output.find('_SEQUENCE=' + primerF) >= 0:
		primer3output = primer3output[primer3output.find('_SEQUENCE=' + primerF):]
		primer3output = primer3output[primer3output.find('\n') - 1:]
		if primer3output[0:primer3output.find(primerR)].count('\n') == 1:
			primer3output = primer3output[primer3output.find('PRIMER_LEFT_'):]
			primer3output = primer3output[primer3output.find('=') + 1:]
			amplicon_start = int(primer3output[0:primer3output.find(',')])
			primer3output = primer3output[primer3output.find('PRIMER_RIGHT_'):]
			primer3output = primer3output[primer3output.find('=') + 1:]
			amplicon_end = int(primer3output[0:primer3output.find(',')]) - len(primerR)
		else:
			primer3output = primer3output[primer3output.find(primerF):]
			primer3output = '_SEQUENCE=' + primer3output

	i = -1
	for line in orig_output.split('\n'):
		i += 1
		if end_line == 0:
			if line.startswith('SEQUENCE_TEMPLATE='):
				sequence = line[len('SEQUENCE_TEMPLATE=') + 1:]
			elif line.startswith('PRIMER_LEFT_') and \
				line.find('_SEQUENCE=' + primerF) > 0 and \
				sequence != '':
				primerF_found = True

			if primerF_found == True:
				if line.startswith('PRIMER_RIGHT_') and \
					line.find('_SEQUENCE=' + primerR) > 0:
					end_line = i
			elif primerF_found == True and line.startswith('PRIMER_RIGHT_') and \
				line.find('_SEQUENCE=' + primerR) <= 0:
				primerF_found = False

	return sequence[amplicon_start - 1 + len(primerF):amplicon_end]

#takes a primer pair and primer3ouput as input
#returns GC-content, primer TM, product size, product TM
def primer_stats(primerF, primerR, primer3output):
	primerF = primerF.upper()
	primerR = primerR.upper()
	temp_output = primer3output.splitlines()
	found = -1

	for i in xrange(len(temp_output)):
		if found == -1:
			if temp_output[i].startswith('PRIMER_LEFT_') and \
				temp_output[i].find('_SEQUENCE=') > 0 and \
				temp_output[i].endswith(primerF):
				if temp_output[i + 1].startswith('PRIMER_RIGHT_') and \
					temp_output[i + 1].find('_SEQUENCE=') > 0 and \
					temp_output[i + 1].endswith(primerR):
					found = temp_output[i][len('PRIMER_LEFT_'):temp_output[i].find('_SEQUENCE')]
		else:
			if temp_output[i].startswith('PRIMER_LEFT_' + found + '_TM='):
				primerF_TM = temp_output[i][temp_output[i].find('=') + 1:]
			elif temp_output[i].startswith('PRIMER_RIGHT_ ' + found + '_TM='):
				primerR_TM = temp_output[i][temp_output[i].find('=') + 1:]
			elif temp_output[i].startswith('PRIMER_LEFT_' + found + '_GC_PERCENT='):
				primerF_GC = temp_output[i][temp_output[i].find('=') + 1:]
			elif temp_output[i].startswith('PRIMER_RIGHT_' + found + '_GC_PERCENT='):
				primerR_GC = temp_output[i][temp_output[i].find('=') + 1:]
			elif temp_output[i].startswith('PRIMER_PAIR_' + found + '_PRODUCT_TM='):
				product_TM = temp_output[i][temp_output[i].find('=') + 1:]

	if found !=- 1:
		return "%.2f" % float(primerF_TM), "%.2f" % float(primerR_TM), "%.2f" % float(primerF_GC), "%.2f" % float(primerR_GC), "%.2f" % float(product_TM)
	else:
		print 'Error: Primer not found in output'
		return '0', '0', '0', '0', '0'

#takes isPCRoutput and searches for the name of the amplicon which is exactly primer,amplicon,primerR
#primerR will be reversed
#amplicon has to be in lower score, primers in upper score
def amplicon_name(primerF, primerR, amplicon, isPCRoutput):
	primerR = primerR.upper()
	primerRold = primerR
	#reverses the reverse primer
	primerR = primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
	temp_output = isPCRoutput.splitlines()
	i = 0
	isPCRamplicon = ''
	while i < len(temp_output):
		if temp_output[i].find(' ' + primerF + ' ') and \
			temp_output[i].find(' ' + primerRold) == len(temp_output) - len(primerRold):
			return temp_output[i][0:temp_output[i].find(' ')]
		if temp_output[i].startswith('>') or temp_output[i].find(';') > -1:
			if isPCRamplicon.replace('\n', '') == primerF + amplicon.lower() + primerR:
				return temp_output[name_line]
			else:
				name_line = i
				isPCRamplicon = ''
		else:
			isPCRamplicon += temp_output[i]
		i += 1
	return ''

#takes input fasta and returns the name of the amplicon which is exactly primer,amplicon,primerR
#primerR will be reversed
def name_from_fasta(primerF, primerR, amplicon, fasta):
	#reverses the reverse primer
	primerR = primerR.upper().replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
	temp_output = fasta.splitlines()
	i = 0
	sequence = ''
	while i < len(temp_output):
		if len(temp_output[i].replace('G', '').replace('C', '').replace('A', '').replace('T', '')) > 0:
			sequence = ''
			name_line = temp_output[i]
		else:
			sequence += temp_output[i]
			if sequence.replace('\n', '').find(primerF + amplicon + primerR) >= 0:
				return name_line
		i += 1

	return ''

#determines the similarity between two oligos
#searches for the longest
def similarity(oligo1, oligo2):
	if len(oligo2) > len(oligo1):
		oligo1, oligo2 = oligo2 , oligo1
	oligo1 = 'X' * len(oligo1) + oligo1 + 'X' * len(oligo1)
	best_score = 0

	for i in xrange(len(oligo1) - len(oligo2)):
		score = 0
		for j in xrange(len(oligo2)):
			if oligo1[i + j] == oligo2[j]:
				score += 1
		if score > best_score:
			best_score = score
	return float(best_score) / float(len(oligo2))

#remove!!!! not in use
#inverses an oligo, i.e. shows the complimentary strand
def inverse_oligo(oligo):
	oligo.replace('A', 't')
	oligo.replace('T', 'a')
	oligo.replace('G', 'c')
	oligo.replace('C', 'g')
	oligo.replace('a', 'A')
	oligo.replace('t', 'T')
	oligo.replace('g', 'G')
	oligo.replace('c', 'C')

	return oligo

#takes primers, amplicon, isPCR output and primer3 output as input
#generates output which can be written to log file
def make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output):
	output = 'Primer pair:, ' + primerF + ', ' + primerR + '\n'
	output += (str('Amplicon: ' + isPCRoutput[isPCRoutput.find('\n') + 2:isPCRoutput.find('bp ') + 2]).replace(' ', ', ') + ', ' + amplicon_name(primerF, primerR, amplicon.lower(), isPCRoutput)).replace('\n', '')
	output += primerF.upper() + amplicon.lower() + primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1] + '\n'
	output += 'primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC\n'
	ampliconGC = str(round(100 * (float(str(primerF + amplicon + primerR).count('G')) + float(str(primerF + amplicon + primerR).count('C'))) / float(len(str(primerF + amplicon + primerR))), 2))
	output += ', '.join(primer_stats(primerF, primerR, primer3_output)) + ', ' + ampliconGC + '\n'

	return output

#checks if an input sequence looks like a proper single fasta sequence
def check_fasta(sequence, fasta_type, strict):

	#strict: boolean, enforces perfect format, i.e. no extra line breaks or spaces, etc.
	#sequence: string the input sequence
	#fasta_type: protein or nucleotide

	passed = True
	fasta_type = fasta_type.upper()

	if fasta_type == 'PROTEIN' or \
		fasta_type == 'AA' or \
		fasta_type.startswith('AMINOACID') or \
		fasta_type.startswith('AMINO ACID'):
		fasta_type = 'P'
		if strict:
			allowed_characters = 'ARNDCEQGHILKMFPSTWYV'
		else:
			allowed_characters = 'ARNDBCEQZGHILKMFPSTWYV'
	elif fasta_type.startswith('NUC') or \
		fasta_type == 'DNA' or \
		fasta_type == 'BASES':
		fasta_type = 'N'
		allowed_characters = 'ATGC'
	else:
		allowed_character = ''

	if not strict:
		sequence = sequence.strip()

	#checks if header is present
	if not sequence.startswith('>'):
		passed = False
	else:
		lines = sequence.split('\n')
		if len(lines) < 2:
			passed = False
		else:
			if not strict:
				lines[0] = ''
				sequence = ''.join(lines)
				sequence = sequence.replace('\n', '')
				sequence = sequence.replace('\r', '')
				sequence = sequence.replace(' ', '')
				sequence = sequence.upper()
				passed = all(i in allowed_characters for i in sequence)
			else:
				if len(sequence) > 2:
					passed = False
				else:
					sequence = lines[1]
					passed = all(i in allowed_characters for i in sequence)

	return passed

def get_primers(sequence):

	global max_primerpairs
	global nested
	#Step 3: creates primer3 input file for each sequence
	output = ''
	stdoutput = ''
	sequences = []
	sequences.append(sequence.split('\n', 1)[0][1:])
	sequences.append(''.join(sequence.split('\n', 1)[1:]).replace('\n', ''))
	if not check_fasta(''.join(sequences), 'NUCLEOTIDE', False):
		stdoutput = 'Sequence did not match FASTA format, no primers were designed'
		output = stdoutput
		return output, stdoutput

	create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats), exclude_list(sequences[1]), '', '')

	stdoutput += 'Primer3 will be started now, please be patient\n'

	primer3_output = ''
	filename = 'primer3_' + makefilename(sequences[0]) + '.txt'
	primer3_input = ''
	with open(primer3_directory + filename, 'ru') as temp_file:
		primer3_input += ''.join(temp_file.readlines())
	temp_file.close()

	stdoutput += 'Primer3 subprocess started\n'
	sys.stdout = open(str(os.getpid()) + ".out", "w")
	process = Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
	process.stdin.write(primer3_input)
	primer3_output += process.communicate()[0] + '\n'

	stdoutput += 'Primer3 finished\n'
	primer3_list = []

	for lines in primer3_output.split('\n'):
		if lines.startswith('SEQUENCE_ID'):
			primer3_list.append(lines)
		elif lines.find('SEQUENCE=') > 0:
			if lines.startswith('PRIMER_LEFT') or lines.startswith('PRIMER_RIGHT'):
				primer3_list.append(lines[lines.find('=') + 1:len(lines)])

	isPCRoutput = ''
	i = 0

	#list of primers which only amplify one amplicon
	accepted_primers = []

	#list of primers which can be used to search for nested primers
	accepted_nested_templates = []

	#accepted_pairs=0
	sequence = ''
	i = 0

	#Step 4: checks all created primers
	sequence = primer3_list[0]
	output += '==========' + '\n' + 'Target:, ' + primer3_list[0][primer3_list[0].find('=') + 1:] + '\n' + '\n'
	primerF_1st = ''
	primerR_1st = ''
	accepted_nested_templates = []


	for i in xrange(1, len(primer3_list), 2):
		if len(accepted_primers) < max_primerpairs:
			primerF = primer3_list[i]
			primerR = primer3_list[i + 1]
			#checks if the primers do not contain repeats, e.g. GAGAGA, not longer than 2x2 repeat
			#if not, runs isPCR to see if they are specific
			if dinucleotide_repeat(primerF) >= 6 or dinucleotide_repeat(primerR) >= 6:
				no_amplicons = 0
				stdoutput += primerF + ' ' + primerR + ' rejected, repeats\n'
			else:
				process = Popen([gfPCR, servername, str(serverport), pcr_location, primerF, primerR, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
				isPCRoutput = primerF + ';' + primerR + '\n' + process.communicate()[0]
				no_amplicons = count_amplicons(isPCRoutput, primerF, primerR)

			i += 1

			#checks if the primer pair amplifies only one amplicon
			if no_amplicons == 1:
				amplicon = get_amplicon_from_primer3output(primerF, primerR, primer3_output)

				#checks if the primer pair amplifies the original target sequence
				accept_primerpair = False
				#should be checked against all primers, not only the first pair
				if check_specificity(primerF, primerR, amplicon, isPCRoutput):
					if len(accepted_primers) == 0:
						primerF_1st = primerF
						primerR_1st = primerR
						accept_primerpair = True
					elif similarity(primerF, primerF_1st) < max_similarity and similarity(primerR, primerR_1st) < max_similarity:
						accept_primerpair = True

					#if the pair is accepted it will be written to the output file
					if accept_primerpair and nested != 1:
						accepted_primers.append(primerF + ',' + primerR)
						output += make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output)
						stdoutput += output + '\n'
					#v1.03
					elif accept_primerpair and nested == 1:
						accepted_nested_templates.append(primerF + ',' + primerR)
			else:
				stdoutput += primerF + ' ' + primerR + ' rejected, not exactly one amplicon\n'
			#checks if not enough suitable primer pairs have been found, then tries to design primers for nested PCR
			#if yes, tries to redesign primers with identical reverse primer but different forward primer

			make_nested_primers = False
			if len(accepted_primers) == 0:
				if i + 1 >= len(primer3_list) and \
					nested != 1:
					stdoutput += 'no suitable primer pairs could be found, consider relaxing the primer3 parameters\n'
				elif i != 0 and \
					i + 1 < len(primer3_list) and \
					nested != 1:
					if primer3_list[i + 1].startswith('SEQUENCE_ID'):
						stdoutput += 'no suitable primer pairs could be found, consider relaxing the primer3 parameters\n'

			elif len(accepted_primers)!= 0 and \
				len(accepted_primers) < max_primerpairs and \
				nested != -1:
				if i + 1 >= len(primer3_list):
					make_nested_primers = True
				elif i != 0 and i + 1 < len(primer3_list):
					if primer3_list[i + 1].startswith('SEQUENCE_ID'):
						make_nested_primers = True

			if make_nested_primers and nested == 0:
				stdoutput += 'trying to find nested primers\n'

				primer3_nested_output = ''
				primer3_input = ''
				primerF_nested = ''
				primerR_nested = ''
				#creates new primer3 file with fixed reverse primer
				create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats), exclude_list(sequences[0]), primerF_1st, primerR_1st)
				filename = 'primer3_' + makefilename(sequences[0]) + '.txt'
				with open(primer3_directory + filename, 'ru') as temp_file:
					primer3_input = ''.join(temp_file.readlines())
				process = Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
				process.stdin.write(primer3_input)
				primer3_nested_output += process.communicate()[0] + '\n'
				stdoutput += 'Primer3 for nested primers finished\n'
				#with open('primer3_nested.txt','w') as temp:
				#	temp.write(primer3_nested_output)
				accept_primerpair = False
				for lines in primer3_nested_output.split('\n'):
					if lines.find('SEQUENCE') > 0:
						if lines.startswith('PRIMER_LEFT'):
							primerF_nested = lines[lines.find('=') + 1:len(lines)]
							primerR_nested = ''
						elif lines.startswith('PRIMER_RIGHT'):
							primerR_nested = lines[lines.find('=') + 1:len(lines)]
							#checks if the new, nested primer pair is specific
							amplicon = get_amplicon_from_primer3output(primerF_nested, primerR_nested, primer3_nested_output)

							if dinucleotide_repeat(primerF_nested) >= 6 or \
								dinucleotide_repeat(primerR_nested) >= 6:
								stdoutput += primerF_nested + ' ' + primerR_nested + ' rejected, repeats\n'
							else:
								process = Popen([gfPCR, servername, str(serverport), pcr_location, primerF_nested, primerR_nested, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
								isPCRoutput_nested = primerF_nested + ';' + primerR_nested + '\n' + process.communicate()[0]

								if check_specificity(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested):
									if similarity(primerF_nested, primerF_1st) < max_similarity:
										stdoutput += primerF_nested + ' ' + primerR_nested + ' found nested primer\n'
										accepted_primers.append(primerF_nested + ',' + primerR_nested)
										output += make_output(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested, primer3_nested_output)
										stdoutput += output + '\n'
										break
									else:
										stdoutput += primerF_nested + ' ' + primerR_nested + ' too similar\n'
								else:
									stdoutput += primerF_nested + ' ' + primerR_nested + ' not specific'

				if len(accepted_primers) < max_primerpairs:
					stdoutput += 'Not enough primer pairs could be found\n'
					max_primerpairs = 0
			####
			#added in v1.03 for forced nested primers
			elif nested == 1 and (i + 1 >= len(primer3_list) or \
				(i != 0 and primer3_list[i + 1].startswith('SEQUENCE_ID'))) and \
				len(accepted_nested_templates) > 0:
				stdoutput += 'forced to trying to find nested primers\n'
				#creates new primer3 file with fixed reverse primer
				for j in xrange(len(accepted_nested_templates)):
					if len(accepted_primers) < max_primerpairs:
						primerF_1st = accepted_nested_templates[j][0:accepted_nested_templates[0].find(',')]
						primerR_1st = accepted_nested_templates[j][accepted_nested_templates[0].find(',') + 1:]
						create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats), exclude_list(sequences[0]), primerF_1st, primerR_1st)
						filename = 'primer3_' + makefilename(sequences[0]) + '.txt'
						primer3_input = ''
						with open(primer3_directory + filename, 'ru') as temp_file:
							primer3_input += ''.join(temp_file.readlines())
						primer3_nested_output = ''
						process = Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
						process.stdin.write(primer3_input)
						primer3_nested_output += process.communicate()[0] + '\n'
						primerF_nested = ''
						primerR_nested = ''
						accept_primerpair = False
						for lines in primer3_nested_output.split('\n'):
							if lines.find('SEQUENCE') > 0:
								if lines.startswith('PRIMER_LEFT'):
									primerF_nested = lines[lines.find('=') + 1:len(lines)]
									primerR_nested = ''
								elif lines.startswith('PRIMER_RIGHT'):
									primerR_nested = lines[lines.find('=') + 1:len(lines)]
									#checks if the new, nested primer pair is specific
									amplicon = get_amplicon_from_primer3output(primerF_nested, primerR_nested, primer3_nested_output)

									if dinucleotide_repeat(primerF_nested) >= 6 or dinucleotide_repeat(primerR_nested) >= 6:
										stdoutput += primerF_nested + ' ' + primerR_nested + ' rejected, repeats\n'
									else:
										process = Popen([gfPCR, servername, str(serverport), pcr_location, primerF_nested, primerR_nested, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
										isPCRoutput_nested = primerF_nested + ';' + primerR_nested + '\n' + process.communicate()[0]

										if check_specificity(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested):
											if similarity(primerF_nested, primerF_1st) < max_similarity:
												stdoutput += primerF_1st + ' ' + primerR_nested + ' found forced nested primer\n'
												accepted_primers.append(primerF_1st + ',' + primerR_1st)
												accepted_primers.append(primerF_nested + ',' + primerR_nested)
												amplicon = get_amplicon_from_primer3output(primerF_1st, primerR_1st, primer3_output)
												process = Popen([gfPCR, servername, str(serverport), pcr_location, primerF_1st, primerR_1st, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
												isPCRoutput = primerF_1st + ';' + primerR_1st + '\n' + process.communicate()[0]
												output += make_output(primerF_1st, primerR_1st, amplicon, isPCRoutput, primer3_output)
												output += make_output(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested, primer3_nested_output)
												stdoutput + =output + '\n'
												break
											else:
												stdoutput += primerF_1st + ' ' + primerR_nested + ' too similar\n'
										else:
											stdoutput += primerF_nested + ' ' + primerR_nested + ' not specific\n'

				stdoutput += 'Primer3 for forced nested primers finished\n'


	if (len(accepted_primers) < max_primerpairs and nested == -1) or (len(accepted_primers) < 2 and nested != -1):
		stdoutput += 'not enough primer pairs found'

	temp = open(str(os.getpid()) + ".tmp", "w")
	temp.write(output)
	temp.write(stdoutput)
	temp.close()
	return output, stdoutput



def start_repeat_finder():
	###########################
	###########################
	#program starts here#######
	###########################
	###########################
	
	#Step 1: checks whether all input files and folders exist, and if the parameters are legal values
	global fasta_filename
	fasta_filename = ''
	global standard_primer_settings_filename
	standard_primer_settings_filename = ''
	global primer3_directory
	primer3_directory = ''
	global primer3_exe
	primer3_exe = ''
	global servername
	servername = ''
	global serverport
	serverport =- 1
	global gfServer
	gfServer = ''
	global gfPCR
	gfPCR = ''
	global max_repeats
	max_repeats = -1
	global max_primerpairs
	max_primerpairs = -1
	global nested
	nested = 0
	global output_filename
	output_filename = 'batchprimer_output.txt'
	global max_threads
	max_threads = 1
	global remove_temp_files
	remove_temp_files = False
	
	import_parameters()
	
	parameters_legal = False
	
	if not os.path.isfile(fasta_filename):
		print 'Fasta file could not be found'
		print fasta_filename
	elif not os.path.isfile(standard_primer_settings_filename):
		print 'Primer3 settings file could not be found'
		print standard_primer_settings_filename
	elif not os.path.isfile(primer3_exe):
		print 'Primer3.exe file could not be found'
		print primer3_exe
	elif not os.path.isfile(gfPCR):
		print 'gfPCR.exe file could not be found'
		print gfPCR
	elif not os.path.isdir(primer3_directory):
		print 'Primer3 directory does not exist'
		print primer3_directory
	elif serverport <= 0:
		print 'Please specificy a legal numerical value for the server port'
	elif int(max_repeats) < 0:
		print 'Please specificy a legal numerical value for the max repeats'
	elif max_primerpairs < 0:
		print 'Please specificy a legal numerical value for the max primer pairs'
	elif max_threads < 1:
		print 'Please specific a legal numerical value for the maximum amount of threads'
	#test if the in-silico PCR server is ready
	elif not test_server(gfServer, servername, serverport):
		print 'gfServer not ready, please start it'
	else:
		parameters_legal = True
	
	if parameters_legal == False:
		exit()
	
	
	#########################################
	#passed all tests, now program can start#
	#########################################
	
	###multiprocess
		print 'program started, please be patient'
	p = Pool(processes = max_threads)

	sequences = []
	for line in open(fasta_filename, 'ru'):
		if line.startswith('>'):
			sequences.append(line)
		else:
			sequences[-1] += line

	results = p.map(get_primers, sequences)
	output = []
	stdoutput = []
	for a in results:
		output.append(a[0])
		stdoutput.append(a[1])
	final_output.write(''.join(output))

	print ''.join(stdoutput)

	final_output.close()
	fasta_file.close()

	print 'done'
if __name__ == "__main__":
	start_repeat_finder()


#Versions
#2015/2/1 V1.00 stable beta version
#2015/2/2 V1.01 fixed bug when no primers where found, added check for location of files and folders, moved import of parameters to a function, changed parameters to int or str, removed unused lines
#2015/2/25 V1.02 changed line feed to work on Linux and Windows
#2015/2/25 V1.03 added nested flag
#2015/2/27 V1.10 rearranged program, get_primers now does most of the job, added OUTPUT flag for output filename, cleaned code [range(0, replace open with xxx as], parallized execution
#replaced range with xrange
#2015/3/15 V1.11 added check_fasta function, rearranged sequence reading loop, added temporary file flag

#To do:
#Add similarity filter to nested=0
#remove temporary files
