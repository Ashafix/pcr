#!/usr/bin/env python
#tests functions used by repeat_finder.py

import unittest
import sys
from repeat_finder import *

class TestCustomMethods(unittest.TestCase):


	def test_read_configfile(self):
		#read_configfile():
		self.assertTrue(True)
	def test_print_help(self):
		self.assertTrue(print_help())
		print_help()
		output = sys.stdout.getvalue().strip()
		self.assertTrue('Usage' in output)
		self.assertTrue('REMOVETEMPFILES' in output)

	def test_test_server(self):
		self.assertFalse(test_server('', '', ''))

	def test_count_amplicons(self):
		#count_amplicons(isPCRoutput, primerF, primerR):
		self.assertTrue(True)
	def test_exclude_list(self):
		test_cases = [['', []], ['AAAAAAAA', []], [12 * 'AT', [11 * 'AT']]]
		for test_case in test_cases:
			self.assertTrue(test_case[1] == exclude_list(test_case[0]))
		
	#def import_parameters(*arguments):
	#def find_repeats(sequence, max_length):
	#def dinucleotide_repeat(sequence):
	def test_dinucleotide_repeat(self):
		test_cases = [['', ''], ['', ''], ['', ''], ['', ''], ['', '']]
		dinucleotide_repeat
	#def create_primer3_file(seq_name, sequence, target, exclude, primerF, primerR):
	def test_makefilename(self):
		test_cases = [['', ''], ['goodname.txt', 'goodname.txt'], ['/usr/bin/badname.txt', 'usrbinbadname.txt'], ['c:\\dir\\badname.txt', 'cdirbadname.txt'], ['name with spaces', 'name_with_spaces']]
		for test_case in test_cases:
			self.assertTrue(makefilename(test_case[0]) == test_case[1])
#def check_specificity(primerF, primerR, targetSequence, isPCRoutput):
#def get_amplicon_from_primer3output(primerF, primerR, primer3output):
#def primer_stats(primerF, primerR, primer3output):
#def amplicon_name(primerF, primerR, amplicon, isPCRoutput):
#def name_from_fasta(primerF, primerR, amplicon, fasta):
	def test_similarity(self):
		test_cases = [['AAA', 'AAA', 1], ['AAA', 'AA', 1], ['AAATTTAAA', 'TTT', 1], ['AAATATAA', 'CTATC', 0.6], ['AAATATAA', '', 0.0], ['AAATATAA', 'ZZZZZZZZZZZ', 0.0], ['AAATATAA', '???????????', 0.0]]
		for test_case in test_cases:
			self.assertTrue(similarity(test_case[0], test_case[1]) == test_case[2])
#def inverse_oligo(oligo):
#def make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output):
#def check_fasta(sequence, fasta_type, strict):
#def get_primers(sequence):


if __name__ == '__main__':
	unittest.main(module = __name__, buffer = True, exit = False)
