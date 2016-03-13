#!/usr/bin/env python

import sys
import os
import subprocess
from multiprocessing import Pool
import logging
import ConfigParser
from time import time, sleep
import urllib, urllib2
import json

#Python2/3 comptability
if sys.version_info < (3, 0):
	from __builtin__ import xrange as range

global ssr_list
ssr_list = ['AAAATTC', 'ATCCCCCCCG', 'AAAATTG', 'ATCCCCCCCC', 'AAATCCCGGGGG', 'AGG', 'ATTCCCCC', 'AAAATTT', 'AATTTTTTCCCC', 'AATTTTTTCCCG', 'TTTTGGG', 'AAACCCCCGGG', 'AAAAATTTGGGG', 'ATTCCCCCCCGG', 'AAAACCCCGGGG', 'ATTCCCCG', 'AAACCCGGG', 'AATCCCGGGGGG', 'AAAACCCGGG', 'AAAATTCCG', 'ATTCCCCGG', 'ATTTCCCCCGGG', 'GG', 'AATTCGGGGGGG', 'ATTTTCCCCGGG', 'TTTCCGGGGGG', 'TTTTTTTGGGG', 'AATCGGGGG', 'TTTGGGGGGG', 'AAAAAAAACGGG', 'CCGGGG', 'TTTTTTCCCCC', 'ATTCCG', 'AATTTCCGGGGG', 'ATTCCC', 'TTTTTTTCCCCC', 'AAAAAAACGGGG', 'CCCCCCGGGGGG', 'TCCCGGG', 'ATGGGGGGG', 'AAAAACC', 'TCCCCCCG', 'AAAAACG', 'TCCCCCCC', 'AAAAAATTTCGG', 'AAAAAAATTTT', 'TTTTTTTTCGGG', 'TTT', 'TTCCCCC', 'TTCCCCG', 'TTC', 'AAAAAAATTTG', 'TTG', 'AAAGGGGG', 'AAAAAAATTTC', 'AATCCCCCCGG', 'AATCCGGGGGGG', 'TTTCCCCCCG', 'AATTTCCGG', 'ATTCCCCGGG', 'AATTGGGGGGG', 'AAAAAAAAAA', 'AAAAAAAAAC', 'AAATTTCCCG', 'TTTTTTCGGGG', 'AAAAAAAAAG', 'AATTTCGG', 'AACCCGGG', 'AAAATTTCCCG', 'TCGG', 'AAAATTTCCCC', 'AAAAAAAAATG', 'AACCCCCGGGGG', 'AAAAAAAAAT', 'ATTCCCCCCCC', 'TTCCCGGGGG', 'ATTCCGGGGG', 'TTCCCCGGG', 'ATTTTTCCC', 'CCGGGGGGGGG', 'AATTTTTGG', 'AAAAAAATTCGG', 'AAAAATTTTTCC', 'AACCCCGGG', 'AAATGG', 'ATCCCCGGGGGG', 'AAGGGGGG', 'AAATTTTTTTTC', 'AAATTTTTTTTG', 'TCCCGGGG', 'ATTTTCCCGG', 'TTTTTTTCGGGG', 'AAGGGGGGGGG', 'AATTCCCGGGGG', 'AATTTTTTTGG', 'AAATTTCCCCCC', 'AAATTTCCCCCG', 'TTTTTCCCCCCC', 'ACCCCGGGGGGG', 'TTTTTCCCCCCG', 'TTCCCCCCGG', 'ATCCGGGGGG', 'ATTCCCGGGGG', 'ACCGGGGG', 'AAAAATTCGG', 'TTTTGGGGGGG', 'ATCCCCCCCCG', 'ATTTCCCCC', 'ATCCCCCCCCC', 'ATTTCCCCG', 'ACCCCGGGGG', 'AATTTTTCCGG', 'TTGGGG', 'TGGGGGG', 'AAAAATTCCCCG', 'AAAAATTCCCCC', 'ATCCCGG', 'AAAACCGGGGGG', 'TCCCCCCCCGGG', 'ATTCG', 'AATTTGGGGGGG', 'AAATTGGGGGGG', 'ATTCC', 'ATCCCCCCGGGG', 'AATTTTCGGG', 'TTTTGGGGG', 'AAAAATTTCGG', 'AAAAAATTTT', 'AAAAAAGGGGGG', 'TTTTCCGGGGG', 'ATTTTTTCC', 'TCGGGGGGGG', 'ATTTTTTCG', 'AAAT', 'AATCCGGGGGG', 'AAAATTCCCC', 'ATTTTTTTTTGG', 'AAAATTCCCG', 'AAAA', 'TCCGGG', 'AAATTCG', 'AAAACGGGGG', 'AAAG', 'AAATTTCCGGGG', 'AAAAAAACCGG', 'ATTTTTC', 'ATTTTG', 'ATTTTTG', 'ATTTTC', 'TTCCCCGGGGGG', 'ATTTTT', 'CCCGGGGGGGGG', 'ATTTTTT', 'ACCCCCCCGG', 'TTCCCCGGGGG', 'ATTTTTCGGGGG', 'AAAAACCGG', 'TTTTTTTTTTGG', 'AAAAATTTTCGG', 'AAATTTGGG', 'ACCGG', 'TTTTTCGGGG', 'ATTTTTGGG', 'TTTTTTCCCCG', 'AAAATCC', 'ATTTTCGG', 'ACCCCCGG', 'CGGG', 'TTTCCCCC', 'AAAATTTTCCGG', 'TTTCCCCG', 'AATCCCCCGG', 'CGGGGG', 'TTTTTCCGGGG', 'AATTTTTGGG', 'ATTCGGGGGG', 'AAAAATCGGG', 'AAATTTTTCGG', 'TTTTTCCCCGG', 'AATTTTGG', 'ATTTTTTTCCCG', 'AAACCGG', 'ATTTTTTTCCCC', 'AAAAATCCCG', 'AAAAATCCCC', 'AAAAAAGG', 'TTTTTCCCCC', 'TTTTTTTCCCCG', 'TTTTTCCCCG', 'AAAAAAAAAATT', 'TTTTTTCCGGGG', 'GGGGGG', 'ATCCG', 'ATCCC', 'AAAATTCCC', 'AAAATTTCGGGG', 'TTTTCCCCCG', 'TTTTCCCCCC', 'AAAAAAAATG', 'AAAAAAAATC', 'AAAAATTCCCC', 'AAATTTGGGGGG', 'AAAAATTCCCG', 'AATTTTTTTTTT', 'AAAAAAAATT', 'AAAAATTTTTTT', 'AATTTGGGG', 'AAAATTCGGGG', 'AACCCC', 'ATTTCCCCCG', 'AACCCG', 'ATCCCCCCCCGG', 'ATTTCCCCCC', 'ATGGGGGG', 'ACCCCCCCCGGG', 'AACCCCCCCCGG', 'AACCCCG', 'AACCCCC', 'TTTTCGGGGGGG', 'AACGGGGGGGG', 'ATTTCGGG', 'AAAACCCCCCGG', 'AATTTCCCCC', 'TTTTTTTTCCCG', 'AATTTCCCCG', 'ATTTTCCGG', 'AAAAAAATCG', 'AAAAAAATCC', 'TTTTCCCGGGG', 'AAAAAATCCGGG', 'TTTTT', 'AAAAAATTTGG', 'TCCCCCGGGGGG', 'AAATCGGGGGGG', 'TTTGGG', 'AATCCCGGGGG', 'ATCCCCGGGG', 'TTTTG', 'TGGGGGGGG', 'AAATTCCCCGG', 'AACCGGGGGG', 'AAAAATGGGGG', 'ATGGG', 'CCCCCCGGGG', 'AAAAAAATGGG', 'CCCC', 'CCCG', 'TTTTTGGGGGGG', 'AATTTTTTTTTC', 'TCCCCGGGGGGG', 'ATTTTCGGGGG', 'AAAATTTCCCCC', 'AAAATTTCCCCG', 'AAAAAAAATTCG', 'AATTTTTTTTTG', 'AACGGGGGGGGG', 'AAAAAAAATTCC', 'TTTTTTCCG', 'TTTTTTCCC', 'ATGGGG', 'ATTTTCCCCCG', 'ATTTTCCCCCC', 'AATTCCCGGG', 'AAAAAAAACCCC', 'AACCCCCC', 'AACCCCCG', 'AAAACCCCC', 'AAAACCCCG', 'AAATTTTCGGG', 'AAACCCCCCGG', 'ATTTTTTTTGG', 'AAACCCCC', 'AAACCCCG', 'AAAACCCCCCG', 'AAAAAAAAAATC', 'AAAACCCCCCC', 'CCCCGGGGGGG', 'AATTTTCCGG', 'AAAATT', 'ATTTTTTTTTTT', 'AAAATTTT', 'AAAAACCCGGGG', 'AAAAAATTGGGG', 'ACCCCCC', 'AAAATG', 'AAAATTTC', 'ACCCCCG', 'AAAATC', 'AAAATTTG', 'AATTTTCCGGG', 'AAAAAGGGG', 'AAAAAAATTGGG', 'ATCCCG', 'AAAAACGGGGG', 'ATCCCC', 'ATGGGGG', 'ACCCGGGG', 'AATTGGG', 'AATTGGGGGG', 'AAAAAATTTGGG', 'AAAACCG', 'AAAACCC', 'AATG', 'TTCCC', 'TTCCG', 'AAAATTTCGG', 'TTCCCCGGGG', 'AATCCCCCGGG', 'AAAATTCGGG', 'AAAAAAAAAAGG', 'AAACCGGGGGGG', 'AATGG', 'AAAATTTTTTCC', 'ATTCCCCCGG', 'AAAATTTTTTCG', 'TTCCGG', 'AAAAAAAAACGG', 'AAAAAAATCCC', 'AATTCCCCCCCG', 'AATTCCCCCCCC', 'TTTCCCCCCC', 'ATTGGGGGGG', 'ACCCCCCGGGGG', 'TTTCGGG', 'AAAATGGGGGG', 'AAAAAAG', 'ATTTCCCGGG', 'AAAAAAA', 'AAAAAAC', 'TTCCCCCGG', 'ACCCCCCCCCC', 'AAAAAAT', 'ACCCCCCCCCG', 'AAAACGGGG', 'AAAATTTTCG', 'ATTTTTTCCCG', 'TTTC', 'AAAATTTTCC', 'ATTTTTTCCCC', 'TTTG', 'CC', 'TTTTTTCC', 'CG', 'AAAAAAAAATT', 'AATTCCCCCG', 'CCCCCC', 'TTTT', 'AAAATCGGG', 'ACCCCCGGGG', 'AATTTTTTTCCC', 'AAAAAAAAT', 'TTTTTTTTTCCG', 'AAATTTCCCC', 'AAAAAAAAA', 'AAAAAAAAC', 'TCCCCGGGG', 'AAAAAAAAG', 'AAAAAAAACC', 'AATTTTTTTCCG', 'AAAAAAAACG', 'AATTTTTTCCG', 'AATTTTTTCCC', 'AAATCCCG', 'AAAAATTTCCCC', 'AAATCCCC', 'AAAAATTTCCCG', 'AAAAATGG', 'TTTTTCGGGGG', 'AATTTTTCCGGG', 'AAAAAATTC', 'AAAAAAAGGGG', 'AAAATCCCG', 'AAAATCCCC', 'AAATCCGGGGGG', 'AAAAAATTT', 'ATGG', 'AATTCCCCG', 'ATCCGGG', 'CCCCCCCCCGGG', 'AAAAAACCC', 'TCCCCCCCCCGG', 'AAAAAACCG', 'AAATCCCCCCCG', 'AAATCCCCCCCC', 'AAATCCCCGGG', 'AAAATCCCCCCG', 'AAAATCCCCCCC', 'ACCGGGG', 'TCCCCCCGGGGG', 'ATTTTGGG', 'AAAACGG', 'TTTTCCGGG', 'AAATCGGGG', 'AAAAATCGG', 'CCCCCCCCCGG', 'CCCCCCCCCCCC', 'CCCCCCCCCCCG', 'AAAAATCCGGG', 'ACCCCCCGGGG', 'AAAATGGGGG', 'AAAATTCGGGGG', 'CCCCCG', 'TTTCCCG', 'AAACCGGGGGG', 'TTTCCCC', 'AATTCCCCC', 'AAAATTCCCCG', 'AAAAAAATCCCG', 'AAAAAAATCCCC', 'ATTTTTCC', 'ATTCCCGGGGGG', 'AAACCCCGGGGG', 'AATTTTTTTC', 'ATTTTTCG', 'ACGGG', 'ATTTTTCCGGG', 'AAAATTGG', 'AAAAATTTCGGG', 'AATTTTCGGGG', 'AATTTCCCCGGG', 'AAAAACCCCCGG', 'TCCCGGGGGGG', 'AATTGG', 'TTTTGG', 'TTTTTTGGGG', 'CCGGGGGG', 'AAATCCCGGG', 'AATTTTGGGG', 'ATTTTTCCG', 'TTTTCCCCCCCG', 'TTCG', 'TTTTCCCCCCCC', 'TTCGGGGGGG', 'TGGGGG', 'AAAAAATTCCGG', 'TTTCCCGGGG', 'AAATTCCCGGGG', 'AAATTCCCGGG', 'TTTGG', 'AAGGG', 'CCCCCGGGGG', 'TTTTTCCCGGG', 'AAACGGG', 'ACCGGGGGGG', 'AAATTTTCC', 'ATTTTTCCCGGG', 'AAATTTTCG', 'AATTTTTGGGG', 'CGGGGGGGG', 'AAAAAATGGG', 'TCGGGGGG', 'AAAAAAAAAGGG', 'AAAAAATCGGGG', 'ACCGGGGGGGG', 'ATTT', 'AATTTTCCG', 'AATTTTCCC', 'AAAAATGGGGGG', 'ATTG', 'ATTC', 'TCCCCGGGGG', 'AAATTTTCCGGG', 'AAATTTTTGGG', 'AAAAAAACCCCC', 'AAAAAAACCCCG', 'AAATTTTTGG', 'ATCCCGGGGGG', 'ATTTTTCCCC', 'ATTTTTCCCG', 'TTTTCCCCCGGG', 'TTCCGGGGGGG', 'ATTTTCGGG', 'AAAATCCG', 'AAAATCCC', 'ATCGGGGGGGG', 'ATTTTCCGGG', 'AATTCGGG', 'TTTCGG', 'TCCCCCCGG', 'CGGGG', 'ATTCCGGGGGG', 'AAATTTTTTTTT', 'AATTTTCGGGGG', 'AAAAACCG', 'AAAAACCC', 'AAAAAAATCGG', 'AATTCCGGGGGG', 'AATCCCCGGG', 'TGGGGGGG', 'TCCGGGGGGGG', 'AATTTTTTGG', 'CCCCCCCCGG', 'TTTCCCCCCCCC', 'GGGGGGGGG', 'TTTCCCCCCCCG', 'AATTTTTTTTCC', 'AAATG', 'AATTTTTTTTCG', 'AAATC', 'TTTTTTTTTCG', 'AAATT', 'TTTTTTTTTCC', 'ATGGGGGGGGG', 'AAAAATTTGGG', 'AAACCCCCCGGG', 'CCCCC', 'CCCCG', 'AAAATCCCGGG', 'TTCC', 'AAAACCCCGGG', 'TTCCCGGGG', 'TTTTTCCCGGGG', 'TTGGGGGG', 'TTTTTGGG', 'TTTCCCCGGGG', 'ATTTTTGGGG', 'AATTTTCCCCGG', 'AATCCCCCCCCG', 'ATTTCGG', 'ATTTCGGGG', 'AATTCCCCCGG', 'AAACCG', 'AAACCC', 'CCCGGGGG', 'ATTTGG', 'AATTTTCCCGG', 'CGGGGGGG', 'TTTCGGGGGG', 'AAATCCCCCCG', 'AAATCCCCCCC', 'AATTCGG', 'TTTTTTCCCCCC', 'TTTTTTCCCCCG', 'ATTTTTTTTCCG', 'ATTTTTTTTCCC', 'AAAATTTTTCCC', 'AAAATTTTTCCG', 'AAATTTGGGG', 'ATTTTTTCCC', 'ATTTTTTCCG', 'AAATCGG', 'AATTTCCCCCC', 'AATTTCCCCCG', 'TTCGGGGGG', 'TTTTCCCCCCC', 'CGGGGGGGGGGG', 'TTTTCCCCCCG', 'AAAAAATTTTCG', 'AAAATTTGGG', 'AAAAAATTTTCC', 'AAAAAAAGGGGG', 'ATTTCCCGGGG', 'ATTCGG', 'AAAAAAATTTTG', 'ATTTTTTTTC', 'ATTTTTTTTG', 'AAAAAATTTTTG', 'ATTTTTTTTT', 'TTTTTTTTC', 'TTTTTTTTG', 'AATTTCCCGGG', 'ACGGGGGGGGG', 'ACGGGGGGGGGG', 'CCGGGGGGGGGG', 'TTTTTTTTT', 'AATTTTGGGGG', 'ATTCCCCCG', 'TTTCCGGGGG', 'AAATCCCGG', 'ATTCCCCCC', 'TTCCGGGGG', 'ATTTTCCCCCGG', 'AAAAAAAATTTC', 'AAAAAAAATTTG', 'AAAAAATC', 'AAAAATGGGG', 'AACCGGGGG', 'AAAAAAAATTTT', 'TTTTTTTCCCGG', 'AAAAAATT', 'AAAAAAATTTTC', 'ATTGGGGGGGG', 'AAATTCCGGGGG', 'ATTTTGGGGGGG', 'TTTCCCCCGGGG', 'AACGGGGG', 'AAAACGGGGGG', 'ATTTGGGGG', 'AAAAAAGGGG', 'ATTTCCCCCGG', 'AACCCCCCCGGG', 'TCCCCCGG', 'AAAATTCCCCCG', 'AAAATTCCCCCC', 'ATTCCGGGGGGG', 'ATTCCGGGG', 'GGGGGGGG', 'AAATTTTCCCCG', 'AAATTTTCCCCC', 'TTTTTCGG', 'AATTTCCCG', 'AATTTCCCC', 'AAAAAAACG', 'AAAAAAACC', 'AAATTTCCGG', 'AACCGGGGGGGG', 'TCCG', 'AATTTCCG', 'CGGGGGGGGG', 'TCCC', 'AATTTCCC', 'AAAAACCCCC', 'CCCCCCCGGG', 'AAAAACCCCG', 'AATTTTTTCCGG', 'AATTTTTCG', 'AAACGGGG', 'ATTCCCGGGG', 'AATTTTTCC', 'CCCCCGGGGGGG', 'CCCCCCCCGGG', 'AAAAAAAACCCG', 'AAAAAATCCC', 'AAAAAATTTTC', 'AAAAAATCCG', 'TTTTCCCGG', 'AAAAAAATTCCC', 'AAAAAAATTCCG', 'AAAAAATTTTT', 'TCCGGGGGGG', 'AAGGGGGGG', 'AAAAATTGGGGG', 'ATTTTTGGGGG', 'TTTTTTTTCC', 'ATTCCCCCCCCG', 'TTTTTTTTCG', 'AAAAAATTCCC', 'AAAAAATTCCG', 'AAAAGGGGGG', 'AATTTTTTTCG', 'AATTTTTTTCC', 'ATTCCCCCCCCC', 'ATTTTCCCCG', 'ATTTTCCCCC', 'TTTCGGGGG', 'TTTCCCCCCGG', 'AAAAATTCCG', 'AAAAATTCCC', 'TTTTTCCCCCGG', 'AAATTCCCCCGG', 'AAAAACCCCGGG', 'ATTTTGGGGGG', 'AATTTTCCGGGG', 'AAAACCCCCCCG', 'ATTTCCCGG', 'AAATCCCCGG', 'AATCCCGGG', 'ATCCGGGGGGG', 'AACGG', 'AAAAATTCCCGG', 'ATTGG', 'AAAAAATTTC', 'TTTTGGGG', 'AAAAAATTTG', 'ATTTTTTGG', 'CCGGGGGGGG', 'AAAAATTTCCG', 'TTGGGGGGGGG', 'AAAAATTTCCC', 'ATG', 'AAAATTCCGG', 'ATC', 'TCCGGGGGG', 'AAAAAAACCCG', 'ATT', 'TTTCCCGGGGG', 'AAAAAAACCCC', 'CGGGGGGGGGG', 'ATTTTTTTTTCG', 'ATTTTTTTTTCC', 'ATTTCCGGGG', 'AAAACCCCCGGG', 'TTTTTTTT', 'ATTTTTTGGGG', 'CCCCGGGGGG', 'AAATTTTTCCCC', 'AAATTTTTCCCG', 'TTTTTTTG', 'TTTTTTTC', 'TCCCCCCCGGG', 'ATCCGGGGGGGG', 'AATTTTTCCCG', 'AAAAAATTCGGG', 'AATTTTTCCCC', 'AAAAACCCC', 'AAAATCCGGG', 'AAAGGG', 'AAAAACCCG', 'AAAAACCGGG', 'AACCCCCCCC', 'ATCCCCCG', 'AACCCCCCCG', 'ATCCCCCC', 'ACGGGGGGG', 'ACCCCCCG', 'ACCCCCCC', 'AAAAAACCGGGG', 'AAAATGG', 'ATTTTCCCGGGG', 'TTTCCCGG', 'ACCG', 'ATTTTTTTCCC', 'ACCC', 'ATTTTTTTCCG', 'ATTTTTTTTCGG', 'ATTTCGGGGG', 'TGG', 'AATTTTC', 'AATTTTG', 'ATTTTTTTCCGG', 'AGGGGGGGGGG', 'AATTTTT', 'AATTCCCCGGGG', 'AATTCCCCCC', 'CCCCCCCC', 'CCCCCCCG', 'ATTTTTCCGGGG', 'TTTTTCCCGG', 'CCCCCGGGG', 'ATCGG', 'AAAATTTTTCC', 'AAAATTTTTCG', 'AAAAAACCCCGG', 'AATTTCCCGGGG', 'TTTTTCCCC', 'CCCCCGGG', 'TTTTTCCCG', 'AAATTCCC', 'AAACCCCCCCGG', 'AAATTCCG', 'AAATTC', 'AAATTG', 'TCCCCCCGGG', 'AAAATCCCCGG', 'AAATTT', 'AAAAATTCCGGG', 'AAAC', 'AAAACCCCCCCC', 'TTGGGGG', 'AACCCCCCCCCC', 'AACCCCCCCCCG', 'AAATGGGG', 'AAATTCC', 'AATTCCCCGGG', 'AAAATTGGGGGG', 'ATCCCCCCCCCC', 'TTTTTTCGGGGG', 'TTCGGG', 'AAAAATCG', 'TTCGGGGG', 'AAAAATCC', 'ATCCCCCGGGGG', 'AAAAAATTGGG', 'TTTTTTTCCC', 'TTTTTTTCCG', 'ATCCCCCCCCCG', 'AAATGGGGGG', 'ATTTCCCCGG', 'AAACCCCGGGG', 'AAATGGGGG', 'TTCCCCCCCCCG', 'TTGGGGGGG', 'TTCCCCCCCCCC', 'AAATGGG', 'TTGGGGGGGGGG', 'AAAAAAAAACC', 'AAAAAAAAACG', 'AAATTTTTT', 'TTTTTTTCCGGG', 'AATTTT', 'TTTTTCGGG', 'ATTTTTTTT', 'AAATTGGG', 'ATTGGG', 'AATTTC', 'TTTTCCGG', 'AATTTG', 'ATTTTTTTG', 'TTTTTTCGG', 'ATTTTTTTC', 'AACCCCGG', 'AATTTTTTTCGG', 'AAACCCCCCCG', 'AATTTGG', 'AAACCCCCCCC', 'ATTTTTTTTTTG', 'AATTCCGGGGG', 'ATTTCCCCCCCC', 'ATTTCCCCCCCG', 'AAACCCGG', 'AAAAAATCCCC', 'TTTCGGGGGGG', 'ATTTT', 'AAAAAATCCCG', 'AATCGGG', 'AAAACCCCCGG', 'AAAAAAAATTT', 'AAATTCCCCC', 'AAAATCGGGGG', 'ATTTC', 'AAATTCCCCG', 'ACCCCCGGGGGG', 'ATTTG', 'AAAAAAAATTC', 'AAAAAAAATTG', 'ATCCGG', 'TCCCCGGG', 'AATTCCGG', 'AAAACCCGG', 'AAAAGGG', 'ATTCCCCCCG', 'ATTCCCCCCC', 'CCCCCCCCC', 'TTTTTTTTCCC', 'TTCCCCCCCCC', 'TTCCCC', 'TTTCCCCGGG', 'TTCCCCCCCCG', 'TTCCCG', 'ATTCGGGGG', 'TTTCCCCCC', 'TTTCCCCCG', 'TTTTTTCCGG', 'ATTTGGGGGG', 'AAAAATTCGGGG', 'AAATTTCC', 'AAAAATTTTGG', 'AATTCCCCCCGG', 'AAATTTCG', 'AAAACCCC', 'AAAACCCG', 'TTTTTTGGGGG', 'ATCCCCCGG', 'TTCCCCCCC', 'AATTTCCCCCCG', 'TTCCCCCCG', 'AATTTCCCCCCC', 'AATTCCCCGG', 'AATTTCGGGGG', 'AATTTTTTTT', 'ATTTTTTTGGGG', 'AAAAAAAACCGG', 'ATTTTTTCCGG', 'AATTTTTTTG', 'ATTTTTTTGGG', 'AAAAAAAATGGG', 'AAAATTTTG', 'AAAAAAACGG', 'TCCCG', 'TCCCC', 'AAAAAAAAGG', 'AAAATTTTT', 'ATTTTTCCCGG', 'AA', 'TTTTTTTTTGGG', 'ATCCCGGGG', 'AATTGGGG', 'ATTCGGGGGGGG', 'TTTTTCCCCGGG', 'ATTTTCGGGGGG', 'AAAATCCGGGG', 'AAACCCGGGG', 'AAAAAAAAATTT', 'AAATCCGG', 'AAAATCG', 'AAATTTTCCC', 'AAATTTTCCG', 'AAAAAAAAATTG', 'AAAAAACCCCG', 'AAAAAAAAATTC', 'AAAAAACCCCC', 'AAATTTCCCGG', 'TCGGG', 'ACCCCCCCCGG', 'AAAAATCCGGGG', 'ATCG', 'ATCC', 'TTCCCCCGGGG', 'AAAAAACGG', 'ATTTCCGGGGGG', 'AATTG', 'ACCCGGGGGG', 'AAAAACCGGGGG', 'AAAGG', 'AATTTTTCGGGG', 'AATTT', 'TCCCCCCCCCCG', 'TCCCCCCCCCCC', 'TTTTTGGGGGG', 'AATTCCGGGG', 'AAATTTCGGG', 'AAATTTCGGGG', 'AACCCCGGGGGG', 'AAAAATCCG', 'AAAAATCCC', 'AAAATTCCCGG', 'ATTTTTTTTTG', 'CCCCCCCGGGGG', 'ATTTTTTTTTC', 'ATTTCCGGG', 'TCCCCCCCCGG', 'ATTTTTTTTTT', 'AAACCCCCGGGG', 'AAAATCCCGG', 'AAAAGG', 'AAAACGGG', 'AAAAAAAATGG', 'AAAAAGGGGG', 'AAAATTCCGGGG', 'TTTCCGGG', 'AAAATTCG', 'AAAATTCC', 'AATTCC', 'AATTCG', 'AATCCGGG', 'AAATTTTCGGGG', 'TTGG', 'AAAAAAAAATC', 'TCCCCCGGGGG', 'AAAACCGGGGG', 'TTTCC', 'ATTGGGGGG', 'TTTCG', 'ATTTTTTTGG', 'AAATTTTGGG', 'TTTGGGG', 'AAAAAACCCC', 'AAAAAACCCG', 'AAAACCCGGGG', 'AATGGGGGGGG', 'ATTTCCGGGGG', 'AAAAATTTTTCG', 'AAATTGGGG', 'AATCCCCCGGGG', 'TTTTCCCCCCGG', 'TTTGGGGG', 'AAAAACCCCCC', 'AAAATTTCC', 'AAAAACCCCCG', 'AAAATTTCG', 'TTTCCGGGGGGG', 'TCCCCCGGG', 'TCCCCCCCGG', 'AACCGGGG', 'AAAAATGGG', 'AAAAAGGGGGGG', 'AATGGGGG', 'ATTTTTCCGG', 'AAAAATTTCG', 'AAAAATTTCC', 'TTTTTCCGGGGG', 'TCCCCGGGGGG', 'TTCCCGGG', 'AAAAATCCCGGG', 'ATTGGGGGGGGG', 'AAAAAAAACCG', 'AAAAAAAACCC', 'AAAAATTTTTC', 'AAAAATTTTTG', 'ACCCCCGGG', 'AAAATCGG', 'TCCCCCCCG', 'TCCCCCCCC', 'AAAAATTTTTT', 'TTTTCCCGGGGG', 'TTTTTTTTTT', 'AAAAAAATCCG', 'TTTTTTTTTC', 'AAATTCCCC', 'TTTGGGGGG', 'AAATTCCCG', 'AAGGGGGGGG', 'AATTTTTTCG', 'AATTTTTTCC', 'TGGGGGGGGGGG', 'AATTTTCCCC', 'AAAATTTTTTTG', 'AAAATTTTTTTC', 'AAAAAAATTTTT', 'AACCCCCCCCG', 'AACCCCCCCCC', 'AAAATTTTTTTT', 'AAAAAATCCCCC', 'AAATCCGGG', 'TTTTTCCGGG', 'TTTTTTGGG', 'CCCGGGGGGGG', 'TTCCCCCCGGGG', 'ATTTTTTCGGGG', 'AACCCCGGGG', 'AACC', 'AAACGGGGGGGG', 'AAAACCCCCC', 'AAAACCCCCG', 'TTTCCG', 'TTTCCC', 'CCCGGGGGGG', 'ATTTGGGGGGGG', 'AATCCGGGG', 'AAAAACCGGGG', 'AAATCCCGGGG', 'AAAAAAAAAAT', 'CCCCGGG', 'TTTTTTG', 'TTTTTTC', 'AAACCGGG', 'AAAAGGGGGGGG', 'AATCCCCCCCGG', 'AAAAAAAAAAG', 'AAAAAAAAAAA', 'AAAAAAAAAAC', 'AATCCGG', 'TTTTTTT', 'AAACGG', 'TCCCCCCGGGG', 'AAAAATCGGGG', 'AAAAGGGGGGG', 'ATTTCG', 'ATTTCC', 'ATCGGG', 'AATTTTCCCCC', 'AATTTTCCCCG', 'AAAAAAAAAATG', 'AAACCCCCGG', 'AATTTTTCGGG', 'ATTCGGGG', 'AAAAAATTCCCG', 'ACGGGG', 'AATTTCCCCGG', 'AAAATTTTTCGG', 'AAAACCGGG', 'AAAAAATTTTGG', 'ATTTTTTCGG', 'TCGGGGGGGGG', 'TTGGG', 'ATCCCCCGGG', 'TTCCCCCG', 'CCCCCGGGGGG', 'AAAATTTTGGG', 'GGGGGGG', 'AATTCCCCCGGG', 'AATGGGG', 'TCCGGGGG', 'ACCCCCCCG', 'ACGGGGG', 'AATTCCC', 'AATTCCG', 'AATCCCCCCCCC', 'ATCGGGGG', 'ATTTTCCCCCCC', 'ATTTTCCCCCCG', 'AAATCCCCG', 'AAATCCCCC', 'AAAAAAAAAAAT', 'AAATTTTTTG', 'ATTTTTTCGGG', 'AAATTTTTTC', 'TCGGGGGGGGGG', 'AAAAAAAAAAAA', 'AAAAAAAAAAAC', 'TTTCGGGGGGGG', 'AAAAAAAAAAAG', 'ATCGGGGGGG', 'TGGGGGGGGG', 'AAATTTTTTT', 'AAAAAAAATCGG', 'AAAAAAAGG', 'TTTTTTTTTCGG', 'AAAAAATTTTTC', 'AAAATGGGGGGG', 'AATTTTGGGGGG', 'ATTTTTGG', 'AGGGGGGGG', 'AAAAAACGGGGG', 'AAATCGGG', 'ATTTCCCCCCG', 'TCCCCCCCGGGG', 'ATTTCCCCCCC', 'AATCCCGG', 'ACCCCCCCGGG', 'AAAATTCCCCGG', 'AAAATTTTTTT', 'AATCCCCGG', 'TTTTCCCCGGGG', 'AAAAAAGGG', 'AAAATTTTTTG', 'AAAATTTTTTC', 'AAATTTTCCCGG', 'AATCGGGGGG', 'TTTTCCC', 'TTTTCCG', 'AAACCCCCG', 'AAACCCCCC', 'AAATTTTTGGGG', 'AAAAACCCGG', 'AAAAAATCGG', 'TTTTCCCCG', 'TTTTCCCCC', 'AAAAAATGGGG', 'ATTTTCG', 'TTTTTTCCGGG', 'TTCGG', 'TTTTTCCGG', 'AAATTTCCCCGG', 'TTTCCCCCGGG', 'ATCCGGGG', 'AAAATTCCGGG', 'ATTTTTTTCG', 'AAAAATTGG', 'AAAAAATTCGG', 'AAAATTGGG', 'AAATTCGGG', 'AAAAT', 'TCGGGG', 'AAAAA', 'AAAAC', 'AAATCGGGGGG', 'AAAAG', 'AAATTTCCCGGG', 'TTTTTGG', 'AGGGGGG', 'TTTCCCCCCCG', 'TTCCGGG', 'TTTCCCCCCCC', 'AAATTTTCCCC', 'ATTCCCC', 'AAATTTTCCCG', 'TTTTTTTTCCG', 'ATTCCCG', 'AAATCCCCCG', 'TTTTGGGGGGGG', 'AAATCCCCCC', 'AAATTCGGGG', 'CCCCCCCCG', 'AATCGG', 'AAAAAATTTCCG', 'AAATCCGGGG', 'AAAAAAAAAACC', 'AAAAACGGGGGG', 'AACCC', 'AAAAAT', 'AACCG', 'AAAAAAAAAACG', 'AAATTTTTTGG', 'ATTTCCCCGGG', 'AAAAAA', 'AAAAAC', 'AAAAAG', 'ATTTTCCGGGGG', 'ATTTTTCGGG', 'TTTTTTTTTTT', 'ACCCGG', 'TTTTTTTTTTC', 'TTTTTTTTTTG', 'TTTTTTTGG', 'AATTTCCGGGG', 'TTTTTTTCCCG', 'AATGGGGGG', 'GGGGGGGGGGG', 'AACCCCCCC', 'AACCCCCCG', 'ACCCCCCCCCCG', 'AAATTCCCCGGG', 'ACCCCCCCCCCC', 'ATTTTTTCCCGG', 'ATTTGGGG', 'AATGGGGGGGGG', 'AAAAAAAATTGG', 'ATCCCCGG', 'AATTCGGGGGG', 'ATTCCCCCGGG', 'ATTGGGGG', 'ATTTTTTTCGG', 'AAAAATCCCCGG', 'ATTTTTTT', 'AAATTTTGGGG', 'TTCCCCGG', 'ATTTTTTC', 'TCGGGGGGG', 'ATTTTTTG', 'AGGGGG', 'ACCCCCCGG', 'AAAATGGG', 'AAAAAAAGGG', 'AAAATTTGGGG', 'AAATTTCCC', 'AAATTTCCG', 'TCG', 'TTTGGGGGGGG', 'TCC', 'ATCCCGGGGG', 'TTTTTTTTGG', 'TTTCCGGGG', 'ATTTTCC', 'AATCCGGGGG', 'AAGGGGGGGGGG', 'ATTTTTTGGGGG', 'AAAAAAATT', 'AAATTGGGGGG', 'AATTTTTTCGGG', 'CCCCCCGG', 'AAAAAAATG', 'AAAAAAATC', 'AAAATTTTTGG', 'ATTTGGGGGGG', 'AAATTCCCCCCC', 'AAATTCCCCCCG', 'AACCCGGGG', 'AAAAATCCCGG', 'AAAAAAAAATGG', 'AAATTCGG', 'AAACCCCCCCCC', 'AAACCCCCCCCG', 'AAAAAACCCCCC', 'AAATTTTTTTCG', 'AAAAAACCCCCG', 'TTTTCGGGG', 'AAATTTTTTTCC', 'ATCCGGGGG', 'AAACCGGGGG', 'AAATTTTTTCCG', 'AAATTTTTTCCC', 'TTTTTCCC', 'CCCGGGGGG', 'TTTTTCCG', 'AAAATCCCCCG', 'AAAATCCCCCC', 'CCCCCGG', 'TTTTTTTCGGG', 'AAAAAAAAGGGG', 'TCCCCCG', 'TCCCCCC', 'TCCCCG', 'TCCCCC', 'AAAAAAAAAGG', 'AAAACCCGGGGG', 'TTTTTTGG', 'ACCCCGGGGGG', 'GGGGGGGGGGGG', 'AAATTTTTTGGG', 'AATTTCGGGGGG', 'AAAAAAATTCG', 'AAAAAAATTCC', 'TTTCCCCGGGGG', 'TTTTTTTTGGGG', 'AAATTTGGGGG', 'ACCCGGGGG', 'ATCCCCGGGGG', 'AAATTTTTTTT', 'AAAATTTTTGGG', 'TTTTCGGG', 'AAATTTTTTTC', 'AACCCCCGGGG', 'AAATTTTTTTG', 'AAAAATTTC', 'AAAAATTTG', 'ATTTTTTTTGGG', 'TTCCCCCCCCGG', 'GGGGGGGGGG', 'AAAAATTTT', 'ATTTTTTGGG', 'TTTTTTTCGG', 'AAATTCCCGG', 'AATTTTTCCCGG', 'AAAAATTCGGG', 'AAAATTTTCGG', 'CCG', 'AACGGG', 'CCC', 'AAAAAAATTTGG', 'TTTTCCCG', 'AAAAAATCC', 'TTTTCCCC', 'AAAAAATCG', 'AAATTCGGGGG', 'TTTTTTCGGG', 'AATGGGGGGG', 'AATTTCC', 'ACCCGGGGGGGG', 'AATTTCG', 'AAAAACGGGG', 'TTTTC', 'AAATTTCGGGGG', 'AACCGGG', 'AATTTCCGGG', 'AACCCCGGGGG', 'AAAATTTTC', 'ATTTCCCC', 'AAAAAACCCGGG', 'ATTTCCCG', 'TTTTCCCGGG', 'AAAAAATCCGG', 'TTTTTTTTCGG', 'CCCCCCCGG', 'AATTTTTTTGGG', 'AATCCCCCCGGG', 'ATTCCCCCCCG', 'AAAAAACGGGG', 'AAAGGGGGGG', 'ATGGGGGGGGGG', 'ATTTTTCCCCCC', 'ATTTTTCCCCCG', 'TTTTGGGGGG', 'AACCCGGGGGG', 'AATTCCCG', 'AATTCCCC', 'AAAATTTCCGGG', 'AAAATTCCCGGG', 'TTCCCCCCCGG', 'AATCGGGG', 'AAAAAATCCCCG', 'ATCCCCGGG', 'ACC', 'TTTTTTCCCG', 'TTTCCCGGGGGG', 'ACG', 'TTTTTTCCCC', 'ATTTTCCCGGG', 'ATCCCCCCGG', 'AAAAATTTTCG', 'AAATTTGG', 'AAAAATTTTCC', 'TTTCCCCGG', 'CCCCGGGG', 'AAAAAAGGGGG', 'TTTTTGGGGG', 'ATTTTGG', 'AATCCCCCCCC', 'AATCCCCCCCG', 'AATTTCCCCCGG', 'AAAACCGG', 'TTCCGGGGGG', 'AAAAAAATTTCC', 'TTTTTTCCCGG', 'AAAAAAATTTCG', 'ACCCGGG', 'AAATTTTTC', 'TTTTTTTTTTTC', 'AAATTTTTG', 'TTTTTTTTTTTG', 'ATTCCCGG', 'TCCGG', 'TTTGGGGGGGGG', 'AAAATTCGG', 'AAAAAAACCG', 'AAATTTCCGGG', 'TTTTTTTTTTTT', 'AAAAAAACCC', 'AAACG', 'ATTTCCCCGGGG', 'AAACC', 'ATGGGGGGGG', 'AAAGGGGGGGGG', 'AAAAAGG', 'AAACGGGGGGG', 'TTGGGGGGGG', 'AAATTTTCGG', 'CCCGGGG', 'TTCCCGG', 'TT', 'AAAAATTT', 'AAAAAATTTCCC', 'AAAAATTG', 'TG', 'AAAAATCCGG', 'AAAAATTC', 'TC', 'AAAAAGGGGGG', 'AC', 'AG', 'ATCCCCCCG', 'ATCCCCCCC', 'AT', 'AAAATTTCCGG', 'TTCCGGGG', 'ACCCCGGGG', 'AAAATTTGGGGG', 'AAATGGGGGGGG', 'AACCCCCGGG', 'AATTTTTCGG', 'AAAAATCGGGGG', 'AGGGGGGGGG', 'ACCCG', 'ATCCCCG', 'ACCGGGGGGGGG', 'ATCCCCC', 'AAATCG', 'AAATCC', 'AAAAAACCCGG', 'AAATTTCCCCG', 'TTTTTTGGGGGG', 'AAATTTCCCCC', 'AAATGGGGGGG', 'AAATTTTGGGGG', 'TCCCCCCCCCG', 'TCCCCCCCCCC', 'TTTTTGGGG', 'ATTCCCCCCGG', 'AAAACC', 'AAAATCCCCG', 'AAAAAATTTTTT', 'AAAACG', 'AAAATCCCCC', 'AAACGGGGG', 'ATTGGGG', 'CCGGGGG', 'ATTTTTTTCC', 'AAAAAATG', 'AAAAAAAATCG', 'TTCCCCCCCC', 'AAAAAAAATCC', 'TTCCCCCCCG', 'AGGG', 'TTTTTTTCCCC', 'AATTCCGGG', 'ATCCCCCCCGG', 'TTTTTCGGGGGG', 'AAAATCCCCGGG', 'ATCCCCCGGGG', 'AAATTTTTCGGG', 'AATTTTTTGGG', 'AAATCCCCCGGG', 'AAACCCGGGGG', 'AATCCCGGGG', 'AAATTGG', 'AAAAATTTGG', 'AAAACCGGGG', 'AAAATTTTTC', 'ACCCCCCCCC', 'CCCGGG', 'AAAATTTTTG', 'ACCCCCCCCG', 'CCCCGGGGGGGG', 'GGG', 'AAAATTTTTT', 'AAAAAACCGG', 'AATTC', 'AAAAAAATCGGG', 'ATTTTTCCCCC', 'ATTTTTCCCCG', 'ACCCC', 'TTTTTTTTTTCG', 'AATTGGGGG', 'TTTTTTTTTTCC', 'ATTTTCCC', 'ATTTTCCG', 'AAAAACCCCGG', 'AAAATTTGG', 'AATTCCCGGGG', 'AAAAGGGGG', 'TCCCCCCCCG', 'TCCCCCCCCC', 'AACCCCCCCGG', 'ATCCCGGG', 'AAACCCCGGG', 'GGGG', 'AATCCCCCCC', 'AATCCCCCCG', 'AAATTTTTCCC', 'TTCCCGGGGGGG', 'AAATTTTTCCG', 'AAATTTTT', 'TGGGG', 'AAAAAAAACGG', 'AATTCGGGGG', 'AAATTTTG', 'AAATTTTC', 'AAACCCG', 'AAAAATTTTTGG', 'AAACCCC', 'TCCCGGGGG', 'TTTTTCCCCCG', 'AAATTCCGG', 'AATCC', 'AATCG', 'AATTCGGGG', 'AAAAAACC', 'AAAAAACG', 'TTCCCCCGGG', 'AAAATTTTCCCG', 'AAAATTTTCCCC', 'TTCCCCCCCGGG', 'AAACCGGGG', 'GGGGG', 'AATCCCC', 'AATTTTGGG', 'AATCCCG', 'AATTGGGGGGGG', 'TTTTCCCCGG', 'AAAAAATCGGG', 'AAATTCCGGG', 'ATTTCCCCCCGG', 'AACCGG', 'AAAAATG', 'AAAAATC', 'AAAACCCCGG', 'TTTTTTTTCCCC', 'AAAAATT', 'AATTTTTTTTG', 'AGGGGGGGGGGG', 'TCCGGGG', 'AAAAAATTGG', 'AAAAAAACCGGG', 'TGGGGGGGGGG', 'AACCCGG', 'AAAAGGGG', 'AATTTCCCGG', 'ACCCCCGGGGG', 'AAAATCGGGG', 'ACCCCCCGGG', 'AATTTGGGGGG', 'TTCCCCCCGGG', 'AATTTGGGGG', 'AATTTTTCCCCG', 'TTTTTTTTGGG', 'AAAAAAATGG', 'CCCCCCGGG', 'AAATTCCCCCG', 'AAAATCGGGGGG', 'AAATTCCCCCC', 'AAAAAATTTCC', 'AAAAAATTTCG', 'AATTTTTCCCCC', 'TTTTTCCCCCC', 'ATTCCCCGGGG', 'AAAATTTTCGGG', 'CCGG', 'AAAAAGGG', 'AACCCCCCGG', 'AAACCCCCCG', 'AAACCCCCCC', 'ATTTTTTTTTTC', 'AAAATTTCCCGG', 'TTTCCCCCCGGG', 'ATTTTCCCG', 'ATTTTCCCC', 'AAGG', 'AAAAAAAATCCG', 'AAAAAAAATCCC', 'AAATCCGGGGG', 'ATTTTCCCCGG', 'CCGGG', 'TTTTCGGGGG', 'TTTCCCGGG', 'AAAAATTTTTTC', 'AAAAATTTTTTG', 'ACGGGGGG', 'ATTCCCCCCGGG', 'ATTTTTTTTCC', 'ATTTTTTTTCG', 'ATCCCCCCCGGG', 'AAATTTT', 'AATT', 'AAAAATTTTT', 'AAAAAATTCC', 'TTTCCCCCGG', 'AAAAAATTCG', 'AATGGG', 'ACCCCGG', 'AATC', 'AAATTTG', 'TCCCCCGGGG', 'AAATTTC', 'TTCGGGGGGGG', 'AAAAATTTTG', 'AAAAATTTTC', 'AAG', 'AAA', 'ACGG', 'AAC', 'AAATTGGGGG', 'AAT', 'TTTTTTTTTCCC', 'TTTTTTCCCGGG', 'ATCCCCCCGGG', 'AACGGGGGG', 'TTTTTC', 'AATTTTTT', 'TTTTTG', 'CCGGGGGGG', 'AATTTTTG', 'AATTTTTC', 'TTTTTT', 'AAAATTTCCG', 'AAAATTTCCC', 'AATTTTTTGGGG', 'AAAATTTTTTGG', 'AATCCCCCC', 'AATCCCCC', 'AACCGGGGGGG', 'TTTCCGG', 'AATCCCCG', 'TTTTCCCCGGG', 'AAAGGGGGG', 'AATCCCCCG', 'ATCCCGGGGGGG', 'AAAAAAAAACCG', 'AAAAAAAAACCC', 'AATCCCCGGGGG', 'AAAAATTCCGG', 'ACCCCCCCGGGG', 'ATTTTTGGGGGG', 'TTTTCGG', 'ATTTTTTCCGGG', 'AAAAATTTTCCC', 'AGGGGGGG', 'AAACCCCGG', 'AAAATTTTGG', 'AAAAATTCG', 'ATTTCCG', 'AAAAATTCC', 'AAAAAACCGGG', 'AACCCGGGGG', 'TTTTTTTGGGGG', 'AAAAAATGGGGG', 'ATTTTTCGG', 'TTTCGGGG', 'TCCCGGGGGGGG', 'AAATTTTTCCGG', 'TTTTTCC', 'TTTTTCG', 'AACGGGG', 'AATTTCGGGG', 'AAAAATTTCCGG', 'AAATTTTCCGG', 'AATTTTTGGGGG', 'TTTTCCGGGG', 'AATTCCCGG', 'ATTCCGG', 'AAAATCCGG', 'ATTTTCGGGG', 'AATTTCGGG', 'ACCGGG', 'AATCCC', 'AATTTGGG', 'AATCCG', 'TTCCGGGGGGGG', 'TGGG', 'AAATCCCCCCGG', 'AAAATCCCCCGG', 'AATTTTTTCGG', 'ATTCCCCCGGGG', 'AAATTTTTTCC', 'AAATTTTTTCG', 'AAAAAATCCCGG', 'AAAATCCGGGGG', 'TCCCGGGGGG', 'ACCCCC', 'TTTTTTTCCGG', 'AAAAAATTTTG', 'ACCCCG', 'AATTTTTCCG', 'CCCCCCCCCCG', 'AATTTTTCCC', 'CCCCCCCCCCC', 'AAAAAAATTC', 'AACCCCCGG', 'AAAAAAATTG', 'TTTTTTTCG', 'TTTTTTTCC', 'CCCCGG', 'AACGGGGGGG', 'ACCCCCCCCCGG', 'AAAAAAATTT', 'CCCCCCCCCCGG', 'ATTCCCGGG', 'ATTCGGGGGGG', 'AAATTCGGGGGG', 'AAAAAAATCCGG', 'AAAAATTGGGG', 'TCGGGGG', 'AAGGGG', 'ATTTTTTCCCCC', 'ATTTTTTCCCCG', 'TCCGGGGGGGGG', 'AAAAACCCGGG', 'AATCCCCGGGG', 'AAAAATTGGG', 'ACCCGGGGGGG', 'ATTTCCCGGGGG', 'AACG', 'AAAAATCCCCCG', 'AAAAATCCCCCC', 'AAACGGGGGG', 'TTTTCG', 'AACCCCCCGGG', 'TTTTCC', 'AAAAACCCCCCC', 'ATTTTTCGGGG', 'AAAAAAAAGGG', 'AAAAAATTCCCC', 'TTTTCGGGGGG', 'TTCCCCCC', 'ACCCCCCCC', 'AAAGGGGGGGG', 'TTCCCCCGGGGG', 'AAAAAACGGG', 'AAATTTTGG', 'CCCCCCCGGGG', 'AAGGGGG', 'CCCCCCCCGGGG', 'TCCCGG', 'AAAAAAACGGG', 'AAAAATCCCCG', 'AAAAATCCCCC', 'AATTTTCGG', 'ATTCCCCGGGGG', 'AAAAAAAAATCG', 'AAAAAAAAATCC', 'CGGGGGG', 'AAATTTTTTTGG', 'TTTTTTTTCCGG', 'AAATTTCGG', 'AAAAACGGG', 'AAAAATTTTGGG', 'AATTTTCCCGGG', 'AAATTTTTTCGG', 'AAAAAAACCCGG', 'AAAACGGGGGGG', 'AAAAAAAA', 'AATCGGGGGGGG', 'AAAAAAAC', 'AAAAAAAG', 'TTCCCGGGGGG', 'AAATTTTTCC', 'ACCCCGGG', 'AAATTTTTCG', 'AAAAAAAT', 'AAAAATTTTCCG', 'CCCCCCG', 'TCCCCGG', 'CCCCCCC', 'AATTTTCCCG', 'ATCGGGG', 'ATTTTCCGGGG', 'AACCCCCCGGGG', 'AAAGGGG', 'AAAATTGGGG', 'AAAATGGGG', 'AATTTTCG', 'ATCGGGGGGGGG', 'AATTTTCC', 'ACGGGGGGGG', 'AAAAACGG', 'ATTTTGGGGG', 'ATTTTTTTCGGG', 'CCCCCCCCCC', 'TTTCCCCCCCGG', 'CCCCCCCCCG', 'AAAAACCCCCCG', 'ATCGGGGGG', 'AATTTTTTTTGG', 'TTTTTTTTTG', 'AAAATTGGGGG', 'AATTTTTTTTC', 'AAAATCCCGGGG', 'AATTTTTTTTT', 'TTTTTTTTTGG', 'AAAAAATGG', 'AAAATTTTCCC', 'AAAATTTTCCG', 'AATTTTTTG', 'AATTTTTTC', 'AAATCCCCGGGG', 'CGG', 'AGGGG', 'CCCGG', 'CCCCGGGGG', 'ATTCCGGG', 'AAAATTTTGGGG', 'AATTTTTTT', 'AAAAAAATTGG', 'AAAAAATTG', 'ATTTCCGG', 'ATTTCCC', 'AATTTTCCCCCG', 'AATTTTCCCCCC', 'AAATCGGGGG', 'ATTTCGGGGGG', 'ATTTCGGGGGGG', 'TTTTCCGGGGGG', 'ACCGGGGGG', 'AATCGGGGGGG', 'AATTCCCCCCC', 'CCCCCCGGGGG', 'AATTCCCCCCG', 'AAAAAAATGGGG', 'AAATTCCGGGG', 'TTTTTTTGGG', 'AAAATTTCGGG', 'TTTTTTCCCCGG', 'ATTTGGG', 'TTCGGGG', 'AAATCCCCCGG', 'AACCCGGGGGGG', 'ATTCGGG', 'AAATCCG', 'AAATCCC', 'ATTTTTCCCCGG', 'TTTTCCCCCGG', 'TTTTTTCG', 'ATTTTGGGG', 'AAAATTCCCCC', 'TTCGGGGGGGGG', 'AAACCCGGGGGG']

started_via_commandline = False

#http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
class StreamToLogger(object):
	"""
	Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, log_level=logging.INFO):
		self.logger = logger
		self.log_level = log_level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.log_level, line.rstrip())

	def flush(self):
		return ''

logging.basicConfig(
	level = logging.DEBUG,
	format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s',
	filename = "python.log",
	filemode = 'a'
)


def read_configfile(config_filename):
	"""
	reads the config file with all global entries
	"""
	global standard_primer_settings_filename
	global primer3_directory
	global primer3_exe
	global servername
	global serverport
	global gfServer
	global gfPCR
	global data_dir
	global run_name
	global max_threads
	config = ConfigParser.RawConfigParser()
	config.read(config_filename)
	for section in config.sections():
		for option in config.options(section):
			if option.upper() == 'PRIMER3_SETTINGS':
				standard_primer_settings_filename = str(config.get(section, option)).strip()
			elif option.upper() == 'PRIMER3_DIRECTORY':
				primer3_directory = str(config.get(section, option)).strip()
			elif option.upper() == 'PRIMER3_EXE':
				primer3_exe = str(config.get(section, option)).strip()
			elif option.upper() == 'SERVERNAME':
				servername = str(config.get(section, option)).strip()
			elif option.upper() == 'SERVERPORT':
				serverport = int(config.get(section, option))
			elif option.upper() == 'GFSERVER':
				gfServer = str(config.get(section, option)).strip()
			elif option.upper() == 'GFPCR':
				gfPCR = str(config.get(section, option)).strip()
			elif option.upper() == 'DATADIR':
				data_dir = str(config.get(section, option)).strip()
			elif option.upper() == 'MAXTHREADS':
				max_threads = int(config.get(section, option))
			elif option.upper() == '-WAITINGPERIOD':
				waiting_period = float(config.get(section, option))
			elif option.upper() == '-TIMEOUT':
				timeout = int(config.get(section, option))
			elif option.upper() == '-RUNNAME':
				run_name = config.get(section, option)
			else:
				print ('getConfig: unknown conf entry: ' + option)

	if standard_primer_settings_filename == '' or \
		primer3_directory == '' or \
		(primer3_exe == '' and remote_server == '') or \
		servername == '' or \
		serverport == '' or \
		gfServer == '' or \
		gfPCR == '' or \
		data_dir == '' or \
		max_threads == 0:
		print ('getConfig: Missing entry')
		return False
	else:
		return {'PRIMER3_SETTINGS': standard_primer_settings_filename, \
			'PRIMER3_DIRECTORY':primer3_directory, \
			'PRIMER3_EXE':primer3_exe, \
			'SERVERNAME':servername, \
			'SERVERPORT':serverport, \
			'GFSERVER':gfServer, \
			'GFPCR':gfPCR, \
			'DATADIR':data_dir, \
			'MAXTHREADS': max_threads}
		#return True

def print_help():
	"""
	Prints a help message with all input parameters
	"""
	print ('Usage')
	print ('-FASTA %filename : Specifies filename of fasta for which repeats and appropriate primers will be searched, e.g. -FASTA BRCA_markers.fa')
	print ('-PRIMER3_SETTINGS %filename : Specifies filename which specifies the settings which are used for searching primers, e.g. -PRIMER3_SETTINGS BRCA_markers_primers.txt')
	print ('-PRIMER3_DIRECTOY %directory : Specifies a directory where the output files will be saved, e.g. PRIMER3_DIRECTORY c:/pcr/BRCA_markers/')
	print ('-PRIMER3_EXE %filename : Specifies the location of the primer3_core.exe, e.g. -PRIMER3_EXE primer3_core.exe')
	print ('-SERVERNAME name : Specifies the name of the isPCR server (usually name of the computer running isPCR), e.g. -SERVERNAME pcrcomputer')
	print ('-SERVERPORT number : Specifies the port which is used to communicate with the isPCR server, e.g. -SERVERPORT 33334')
	print ('-MAXREPEATS number : Specifies the maximum length of repeats to search, e.g. -MAXREPEATS 3, searches for repeats of di- and trinucleotides')
	print ('-PRIMERPAIRS number : Specifies the number of suitable primer pairs which will be returned')
	print ('-GFSERVER filename : Specifies the location of the gfServer.exe')
	print ('-GFPCR filename : Specifies the location of the gfPCR.exe')
	print ('-MAX_SIMILARITY number : Specifies the maximal similarity for two primer pairs in order to be accepted, from 0 to 1, default = 0.5')
	print ('-@ filename : Specifies a file which list the above mentioned arguments, arguments used with -ARGUMENT will overwrite the arguments in the file')
	print ('-NESTED : Specifies whether the program should search for nested primers if not enough pairs have been found (0), never search (-1) or always search for primers (1)')
	print ('-OUTPUT filename : Specifies the output filename where all the primers and target will be saved, default: batchprimer_output.txt')
	print ('-MAXTHREADS number : Specifies how many threads are started in parallel, should be less than your number of CPU cores')
	print ('-REMOVETEMPFILES boolean : Specifies whether temporary files (e.g. Primer3 input and output) will be deleted after the program finishes. Default is FALSE')
	print ('-SHUTDOWN number : Shuts the isPCR server down after ### minutes, e.g. -SHUTDOWN 50, the server will be shutdown 50 minutes after the first job was started')
	print ('-REMOTESERVER string : Specifies the URL of a server which can run primer3 via a REST API')
	print ('-WAITINGPERIOD float : Specifies the time in seconds between server ping when a remote server is started, default = 0.25')
	print ('-TIMEOUT integer : Specifies the time in seconds until a remote server start is declared unsuccesful, default = 120')
	print ('-RUNNAME string : Specifies the name of the run, only used for identifying jobs on the remote server')

def test_server(gfServer, servername, serverport):
	"""
	tests the gfServer and returns True if the server is working
	"""

	command_line = gfServer + ' status ' + servername + ' ' + str(serverport)
	try:
		gfServer_response = subprocess.check_output([command_line], shell = True, stderr = subprocess.STDOUT)
	except:
		return False

	if gfServer_response.startswith('Couldn'):
		return False
	elif 'version' in gfServer_response and \
		'port' in gfServer_response and \
		'host' in gfServer_response and \
		'type' in gfServer_response:
		return True
	else:
		return False

def count_amplicons(isPCRoutput, primerF, primerR):
	"""
	Takes a list of isPCRoutputs and counts the numbers of amplicons for a primer pair
	"""
	if (not primerF in isPCRoutput) and (not primerR in isPCRoutput) > -1:
		return -1
	else:
		startpoint = isPCRoutput.find(primerF + ';' + primerR)
		isPCRfragment = isPCRoutput[startpoint:]
		if isPCRfragment.find(';', len(primerF) + len(primerR) + 2) > -1:
			isPCRfragment = isPCRfragment[0:isPCRfragment.find(';', len(primerF) + len(primerR) + 2)]
			return isPCRfragment.count('>')
		else:
			return isPCRfragment.count('>')

def exclude_list(sequence):
	"""
	Creates a list of sequences which should be excluded from primer binding sites
	"""
	to_exclude = []
	sequence = sequence.upper()
	for ssr in ssr_list:
		if len(ssr) <= 3:
			max_length = 0
			for i in range(1, len(sequence) / 2):
				if ssr * i in sequence and i * len(ssr) >= 9:
					max_length = i
			if max_length > 0:
				to_exclude.append(ssr * max_length)
	return to_exclude

def import_parameters(*arguments):
	"""
	imports parameters from commandline
	"""
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
	global data_dir
	global max_similarity
	global shutdown
	global remote_server
	global run_name
	global timeout
	global started_via_commandline
	shutdown = -1
	remote_server = ''
	waiting_period = 0.25
	timeout = 120
	max_similarity = 0.5

	data_dir = './'
	input_args = []
	if len(sys.argv) > 1 or len(arguments) == 0:
		if '-help' in str(sys.argv) > -1:
			print_help()
			sys.exit()
		else:
			input_args = sys.argv
	if not started_via_commandline and len(arguments) > 0:
		for argument in arguments[0][0]:
			input_args.append(argument)

	#reads config file
	for i in range(len(input_args)):
		if str(input_args[i]).startswith('-@'):
			read_configfile(input_args[i + 1])

	#reads named arguments
	for i in range(len(input_args)):
		if str(input_args[i]).upper() == '-FASTA':
			fasta_filename = input_args[i + 1]
		elif str(input_args[i]).upper() == '-PRIMER3_SETTINGS' or \
			str(input_args[i]).upper() == '-PRIMER_SETTINGS':
			standard_primer_settings_filename = input_args[i + 1]
		elif str(input_args[i]).upper() == '-PRIMER3_DIRECTORY' or \
			str(input_args[i]).upper() == '-PRIMER_DIRECTORY':
			primer3_directory = input_args[i + 1]
		elif str(input_args[i]).upper() == '-PRIMER3_EXE':
			primer3_exe = input_args[i + 1]
		elif str(input_args[i]).upper() == '-SERVERNAME':
			servername = input_args[i + 1]
		elif str(input_args[i]).upper() == '-SERVERPORT':
			serverport = int(input_args[i + 1])
		elif str(input_args[i]).upper() == '-MAXREPEATS':
			max_repeats = int(input_args[i + 1])
		elif str(input_args[i]).upper() == '-PRIMERPAIRS':
			max_primerpairs = int(input_args[i + 1])
		elif str(input_args[i]).upper()=='-GFSERVER':
			gfServer = input_args[i + 1]
		elif str(input_args[i]).upper() == '-GFPCR':
			gfPCR = input_args[i + 1]
		elif str(input_args[i]).upper() == '-NESTED':
			nested = int(input_args[i + 1])
		elif str(input_args[i]).upper() == '-OUTPUT':
			output_filename = input_args[i + 1]
		elif str(input_args[i]).upper() == '-MAXTHREADS':
			max_threads = int(input_args[i + 1])
		elif str(input_args[i]).upper() == '-REMOVETEMPFILES':
			remove_temp_files = bool(input_args[i + 1])
		elif str(input_args[i]).upper() == '-DATADIR':
			data_dir = input_args[i + 1]
		elif str(input_args[i]).upper() == '-MAX_SIMILARITY':
			max_similarity = float(input_args[i + 1])
		elif str(input_args[i]).upper() == '-SHUTDOWN':
			shutdown = int(input_args[i + 1])
		elif str(input_args[i]).upper() == '-REMOTESERVER':
			remote_server = input_args[i + 1]
		elif str(input_args[i]).upper() == '-RUNNAME':
			run_name = input_args[i + 1]
		elif str(input_args[i]).upper() == '-WAITINGPERIOD':
			waiting_period = float(input_args[i + 1])
		elif str(input_args[i]).upper() == '-TIMEOUT':
			timeout = int(input_args[i + 1])
	if (fasta_filename == '' or \
		standard_primer_settings_filename == '' or \
		primer3_directory == '' or \
		primer3_exe == '' or \
		servername == '' or \
		serverport == -1 or \
		max_repeats == -1 or \
		gfServer == '' or \
		gfPCR == '' or \
		abs(nested) > 1):
		print ('Input arguments')
		print ('fasta_filename: ' + fasta_filename)
		print ('standard_primer_settings_filename: ' + standard_primer_settings_filename)
		print ('primer3_directory: ' + primer3_directory)
		print ('primer3_exe: ' + primer3_exe)
		print ('servername: ' + servername)
		print ('serverport: ' + str(serverport))
		print ('max_repeats: ' + str(max_repeats))
		print ('gfServer: ' + gfServer)
		print ('gfPCR: ' + gfPCR)
		print ('nested: ' + str(nested))
		print ('Missing arguments!\n\n')
		print_help()
		exit()

	return True

def find_repeats(sequence, max_length):
	"""
	finds the longest repeat in a given sequence
	max_length of repeat unit
	"""
	longest_repeat = ''

	for ssr in ssr_list:
		if len(ssr) <= int(max_length):
			i = 1
			while ssr * i in sequence:
				i += 1
			i += -1
			if len(ssr * i) > len(longest_repeat) and i > 1:
				longest_repeat = ssr * i

	return longest_repeat

def dinucleotide_repeat(sequence):
	"""
	finds the length of dinucleotide repeats, i.e. ACTAGAGAGTCA would return 6
	"""
	nucleotides = 'ATGC'
	max_repeat = 0
	for i in range(4):
		for j in range(4):
			n = 1
			while ((nucleotides[i] + nucleotides[j]) * n) in sequence:
				n += 1
			if n - 1 > max_repeat:
				max_repeat = n - 1
	return max_repeat * 2

def create_primer3_file(seq_name, sequence, target, exclude, primerF, primerR):
	"""
	creates the input file for primer3
	if primerF and primerR are given, primerR is kept fixed and primerF is excluded, useful for nested PCR
	"""
	if len(target) >= len(sequence) or (not target in sequence):
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

def makefilename(old_name):
	"""
	cleans a filename
	"""
	old_name = old_name.replace(' ', '_')
	old_name = old_name.translate(None, '+=!/\<>:"|?*\'')
	return old_name

def check_specificity(primerF, primerR, targetSequence, isPCRoutput):
	"""
	takes a primer pair, a input sequence for which the primers were designed and checks in the isPCRoutput if the target sequence is amplified or something else
	also checks if the number of amplicons is exactly one
	"""
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
			if (' ' + primerF + ' ' + primerR + '\n') in line and \
				line.startswith('>'):
				found = True
		elif found == True and (not line.startswith('>') and \
			line.find(';') == -1):
			isPCRamplicon += line
		elif line.startswith('>') or ';' in line and \
			found == True:
			i = len(temp_output)
		i += 1

	if isPCRamplicon == '':
		return False
	else:
		isPCRamplicon = isPCRamplicon.replace('\n', '')
		isPCRamplicon = isPCRamplicon[len(primerF):]
		isPCRamplicon = isPCRamplicon[0:len(isPCRamplicon) - len(primerR)]

		if isPCRamplicon.upper() in targetSequence.upper():
			return True
		else:
			return False

def get_amplicon_from_primer3output(primerF, primerR, primer3output):
	"""
	takes primer3output and returns the amplicon based on primerF and primerR bindingsites and input sequence
	returns the amplicon without the primers
	"""
	amplicon_start = 0
	primerF_found = False
	sequence = ''
	end_line = 0
	orig_output = primer3output

	while amplicon_start == 0 and ('_SEQUENCE=' + primerF) in primer3output:
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
				('_SEQUENCE=' + primerF) in line and \
				sequence != '':
				primerF_found = True

			if primerF_found == True:
				if line.startswith('PRIMER_RIGHT_') and \
					('_SEQUENCE=' + primerR) in line:
					end_line = i
			elif primerF_found == True and line.startswith('PRIMER_RIGHT_') and \
				line.find('_SEQUENCE=' + primerR) <= 0:
				primerF_found = False

	return sequence[amplicon_start - 1 + len(primerF):amplicon_end]

def primer_stats(primerF, primerR, primer3output):
	"""
	takes a primer pair and primer3output as input
	returns GC-content, primer TM, product size, product TM
	"""
	primerF = primerF.upper()
	primerR = primerR.upper()
	temp_output = primer3output.splitlines()
	found = -1

	for i in range(len(temp_output)):
		if found == -1:
			if temp_output[i].startswith('PRIMER_LEFT_') and \
				'_SEQUENCE=' in temp_output[i] and \
				temp_output[i].endswith(primerF):
				if temp_output[i + 1].startswith('PRIMER_RIGHT_') and \
					'_SEQUENCE=' in temp_output[i + 1] and \
					temp_output[i + 1].endswith(primerR):
					found = temp_output[i][len('PRIMER_LEFT_'):temp_output[i].find('_SEQUENCE')]
		else:
			if temp_output[i].startswith('PRIMER_LEFT_' + found + '_TM='):
				primerF_TM = temp_output[i][temp_output[i].find('=') + 1:]
			elif temp_output[i].startswith('PRIMER_RIGHT_' + found + '_TM='):
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
		print (run_name + ' Error: Primer not found in output')
		return '0', '0', '0', '0', '0'

def amplicon_name(primerF, primerR, amplicon, isPCRoutput):
	"""
	takes isPCRoutput and searches for the name of the amplicon which is exactly primer,amplicon,primerR
	primerR will be reversed
	amplicon has to be in lower score, primers in upper score
	"""
	primerR = primerR.upper()
	primerRold = primerR
	#reverses the reverse primer
	primerR = primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
	temp_output = isPCRoutput.splitlines()
	i = 0
	isPCRamplicon = ''
	while i < len(temp_output):
		if ' ' + primerF + ' ' in temp_output[i] and \
			temp_output[i].find(' ' + primerRold) == len(temp_output) - len(primerRold):
			return temp_output[i][0:temp_output[i].find(' ')]
		if temp_output[i].startswith('>') or ';' in temp_output[i]:
			if isPCRamplicon.replace('\n', '') == primerF + amplicon.lower() + primerR:
				return temp_output[name_line]
			else:
				name_line = i
				isPCRamplicon = ''
		else:
			isPCRamplicon += temp_output[i]
		i += 1
	return ''

def name_from_fasta(primerF, primerR, amplicon, fasta):
	"""
	takes input fasta and returns the name of the amplicon which is exactly primer,amplicon,primerR
	primerR will be reversed
	"""
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
			if (primerF + amplicon + primerR) in sequence.replace('\n', ''):
				return name_line
		i += 1

	return ''

def similarity(oligo1, oligo2):
	"""
	determines the similarity between two oligos
	searches for the longest overlap
	X is used a placeholder, so it will match any character
	"""
	if len(oligo2) > len(oligo1):
		oligo1, oligo2 = oligo2 , oligo1
	if len(oligo1) == 0 or len(oligo2) == 0:
		return float(0)
	oligo1 = 'X' * len(oligo1) + oligo1 + 'X' * len(oligo1)
	best_score = 0

	for i in range(len(oligo1) - len(oligo2)):
		score = 0
		for j in range(len(oligo2)):
			if oligo1[i + j] == oligo2[j]:
				score += 1
		if score > best_score:
			best_score = score
	return float(best_score) / float(len(oligo2))

def make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output):
	"""
	takes primers, amplicon, isPCR output and primer3 output as input
	generates output which can be written to log file
	"""
	output = 'Primer pair:, ' + primerF + ', ' + primerR + '\n'
	output += (str('Amplicon: ' + isPCRoutput[isPCRoutput.find('\n') + 2:isPCRoutput.find('bp ') + 2]).replace(' ', ', ') + ', ' + amplicon_name(primerF, primerR, amplicon.lower(), isPCRoutput)).replace('\n', '')
	output += primerF.upper() + amplicon.lower() + primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1] + '\n'
	output += 'primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC\n'
	ampliconGC = str(round(100 * (float(str(primerF + amplicon + primerR).count('G')) + float(str(primerF + amplicon + primerR).count('C'))) / float(len(str(primerF + amplicon + primerR))), 2))
	output += ', '.join(primer_stats(primerF, primerR, primer3_output)) + ', ' + ampliconGC + '\n'

	return output


def check_fasta(sequence, fasta_type, strict):
	"""
	checks if an input sequence looks like a proper single fasta sequence
	strict: boolean, enforces perfect format, i.e. no extra line breaks or spaces, etc.
	sequence: string the input sequence
	fasta_type: protein or nucleotide
	"""
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
	global run_name
	#Step 3: creates primer3 input file for each sequence
	output = ''
	stdoutput = ''
	sequences = []

	sequences.append(sequence.split('\n', 1)[0][1:])
	sequences.append(''.join(sequence.split('\n', 1)[1:]).replace('\n', ''))

	if not check_fasta('>' + '\n'.join(sequences), 'NUCLEOTIDE', False):
		stdoutput += 'Sequence did not match FASTA format, no primers were designed\n'
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
	if remote_server != '':
		local_run_name = run_name
		local_run_name += '_' + str(os.getpid())
		baseurl = remote_server + ':8003'

		params = urllib.urlencode({'run_name': local_run_name, 'primer3_input': primer3_input})
		primer3_request = urllib2.Request(baseurl + '/primer3', params)
		primer3_response = urllib2.urlopen(primer3_request)
		primer3_status = ''

		max_time = 1200
		waiting_period = 2
		while primer3_status != 'finished' and max_time > 0:
			sleep(waiting_period)
			max_time -= waiting_period
			params = urllib.urlencode({'run_name': local_run_name})
			primer3_url = urllib2.urlopen(baseurl + '/job_status' + '?' + params)
			primer3_response = primer3_url.read()
			if 'job_status' in primer3_response:
				try:
					primer3_status = json.loads(primer3_response)['job_status'][local_run_name]
				except:
					primer3_status = ''
		primer3_url = urllib2.urlopen(baseurl + '/job_results' + '?' + params)
		primer3_output = primer3_url.read()
		while '\\n' in primer3_output:
			primer3_output = primer3_output.replace('\\n', '\n')
		primer3_output = primer3_output[1:-1] + '\n'
	else:
		sys.stdout = open(str(os.getpid()) + ".out", "w")
		process = subprocess.Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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
	print (run_name + " ##################")

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
	output += '==========' + '\n'
	output += 'Target:, ' + primer3_list[0][primer3_list[0].find('=') + 1:] + '\n\n'
	primerF_1st = ''
	primerR_1st = ''
	accepted_nested_templates = []
	for i in range(1, len(primer3_list), 2):
		if len(accepted_primers) < max_primerpairs:
			primerF = primer3_list[i]
			primerR = primer3_list[i + 1]
			#checks if the primers do not contain repeats, e.g. GAGAGA, not longer than 2x2 repeat
			#if not, runs isPCR to see if they are specific
			if dinucleotide_repeat(primerF) >= 6 or dinucleotide_repeat(primerR) >= 6:
				no_amplicons = 0
				stdoutput += primerF + ' ' + primerR + ' rejected, repeats\n'
			else:
				process = subprocess.Popen([gfPCR, servername, str(serverport), pcr_location, primerF, primerR, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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
			#checks if not enough suitable primer pairs have been found
			#then tries to design primers for nested PCR
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
				process = subprocess.Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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
								process = subprocess.Popen([gfPCR, servername, str(serverport), pcr_location, primerF_nested, primerR_nested, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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
				for j in range(len(accepted_nested_templates)):
					if len(accepted_primers) < max_primerpairs:
						primerF_1st = accepted_nested_templates[j][0:accepted_nested_templates[0].find(',')]
						primerR_1st = accepted_nested_templates[j][accepted_nested_templates[0].find(',') + 1:]
						create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats), exclude_list(sequences[0]), primerF_1st, primerR_1st)
						filename = 'primer3_' + makefilename(sequences[0]) + '.txt'
						primer3_input = ''
						with open(primer3_directory + filename, 'ru') as temp_file:
							primer3_input += ''.join(temp_file.readlines())
						primer3_nested_output = ''
						process = subprocess.Popen(primer3_exe, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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
										process = subprocess.Popen([gfPCR, servername, str(serverport), pcr_location, primerF_nested, primerR_nested, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
										isPCRoutput_nested = primerF_nested + ';' + primerR_nested + '\n' + process.communicate()[0]

										if check_specificity(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested):
											if similarity(primerF_nested, primerF_1st) < max_similarity:
												stdoutput += primerF_1st + ' ' + primerR_nested + ' found forced nested primer\n'
												accepted_primers.append(primerF_1st + ',' + primerR_1st)
												accepted_primers.append(primerF_nested + ',' + primerR_nested)
												
												process = subprocess.Popen([gfPCR, servername, str(serverport), pcr_location, primerF_1st, primerR_1st, 'stdout'], stdout = subprocess.PIPE, stdin = subprocess.PIPE)
												isPCRoutput = primerF_1st + ';' + primerR_1st + '\n' + process.communicate()[0]
												amplicon = get_amplicon_from_primer3output(primerF_1st, primerR_1st, primer3_output)
												output += make_output(primerF_1st, primerR_1st, amplicon, isPCRoutput, primer3_output)
												#should fix the problem with the doubled amplicon
												amplicon = get_amplicon_from_primer3output(primerF_nested, primerR_nested, primer3_nested_output)
												output += make_output(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested, primer3_nested_output)
												stdoutput += output + '\n'
												break
											else:
												stdoutput += primerF_1st + ' ' + primerR_nested + ' too similar\n'
										else:
											stdoutput += primerF_nested + ' ' + primerR_nested + ' not specific\n'

				stdoutput += 'Primer3 for forced nested primers finished\n'


	if (len(accepted_primers) < max_primerpairs and nested == -1) or (len(accepted_primers) < 2 and nested != -1):
		stdoutput += 'not enough primer pairs found\n'

	temp = open(str(os.getpid()) + ".tmp", "w")
	temp.write(output)
	temp.write(stdoutput)
	temp.close()
	return output, stdoutput

def start_remote_server(*arguments):
	"""
	Starts a remote AWS instance where primer3 and gfServer run
	Returns the remote server URL if the server was started succesfully
	Returns '' if the start failed
	"""
	stdout_logger = logging.getLogger('STDOUT')
	sl = StreamToLogger(stdout_logger, logging.INFO)
	sys.stdout = sl

	stderr_logger = logging.getLogger('STDERR')
	sl = StreamToLogger(stderr_logger, logging.ERROR)
	sys.stderr = sl

	import boto3
	import socket
	if arguments:
		if len(arguments) > 4:
			gfServer = arguments[0]
			servername = arguments[1]
			serverport = arguments[2]
			timeout = arguments[3]
			server_extension = arguments[4]
		waiting_period = 0.25
	else:
		global servername
		global hostname
		global compute_host
		global timeout
	print ('Start remote server<br>')
	print ('Server name: ' + servername)
	print ('<br>gfServer: ' + gfServer)
	print ('<br>Server port: ' + str(serverport))
	print ('<br>Time out: ' + str(timeout))

	aws = read_aws_conf()
	session = boto3.session.Session(aws_access_key_id = aws['aws_access_key_id'],
		aws_secret_access_key = aws['aws_secret_access_key'],
		region_name = aws['region_name'])
	ec2 = session.resource('ec2')

	instances = ec2.instances.all()
	if len(list(instances)) < 2:
		print ('No second AWS instance was found!')
		return ''

	hostname = socket.gethostbyaddr(socket.gethostname())[0]
	compute_host = ''
	for instance in instances:
		instance_name = ''
		if instance.private_dns_name != hostname and compute_host == '':
			#get the base hostname
			for tag in instance.tags:
				if 'Value' in tag:
					if 'Key' in tag.keys() and 'Value' in tag.keys():
						if tag['Key'] == 'Name':
							#checks if the right instance type was selected
							if server_extension in tag['Value']:
								instance_name = tag['Value']
			if instance_name == servername + server_extension:
				servername = instance.private_dns_name
				print ('<br>' + 'Servername: ' + servername + '<br>')
				compute_host = instance.id
				instance.start()
				#wait until the instance is up and running
				local_timeout = timeout
				while instance.state['Code'] != 16 and local_timeout > 0:
					sleep(waiting_period)
					local_timeout += -waiting_period
				if local_timeout < 0:
					print ('Server start was unsuccesful, the timeout period was exceeded')
					return ''
				if not test_server(gfServer, servername, serverport):
					print ('Server start was successful, but gfServer does not respond')
					return ''
				else:
					return instance_name
	return ''

def read_aws_conf():
	"""
	reads the AWS credentials
	returns a dict with the values from the credentials file
	"""
	aws = {}
	locations = ['/var/www/data/', '/home/ubuntu/.aws/']
	for location in locations:
		if os.path.isfile(location + 'credentials'):
			try:
				credentials = open(location + 'credentials', 'r')
				aws['region_name'] = 'eu-central-1'
				for line in credentials.readlines():
					if '=' in line:
						cells = line.split('=')
						aws[cells[0].strip()] = cells[1].strip()
				credentials.close()
				return aws
			except:
				pass
	return aws

def start_repeat_finder(started_via_commandline, *arguments):

	###########################
	###########################
	###program starts here#####
	###########################
	###########################

	#Step 1: checks whether all input files and folders exist, and if the parameters are legal values
	global max_similarity
	max_similarity = 0.5
	global pcr_location

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
	global hostname
	hostname = ''
	global compute_host
	compute_host = ''
	global run_name
	run_name = ''
	global timeout
	timeout = 120
	#redirects output if not started via commandline
	if started_via_commandline:
		import_parameters()
	else:
		stdout_logger = logging.getLogger('STDOUT')
		sl = StreamToLogger(stdout_logger, logging.INFO)
		sys.stdout = sl

		stderr_logger = logging.getLogger('STDERR')
		sl = StreamToLogger(stderr_logger, logging.ERROR)
		sys.stderr = sl
		import_parameters(arguments)

	#all input parameters are valid
	parameters_legal = False

	if not os.path.isfile(fasta_filename):
		print (run_name + ' Fasta file could not be found')
		print (fasta_filename)
	elif not os.path.isfile(standard_primer_settings_filename):
		print (os.path.isfile(standard_primer_settings_filename))
		print (run_name + ' Primer3 settings file could not be found')
	elif not os.path.isfile(primer3_exe):
		print (run_name + ' Primer3.exe file could not be found')
		print (primer3_exe)
	elif not os.path.isfile(gfPCR):
		print (run_name + ' gfPCR.exe file could not be found')
		print (gfPCR)
	elif not os.path.isdir(primer3_directory):
		print (run_name + ' Primer3 directory does not exist')
		print (primer3_directory)
	elif serverport <= 0:
		print (run_name + ' Please specificy a legal numerical value for the server port')
	elif int(max_repeats) < 0:
		print (run_name + ' Please specificy a legal numerical value for the max repeats')
	elif max_primerpairs < 0:
		print (run_name + ' Please specificy a legal numerical value for the max primer pairs')
	elif max_threads < 1:
		print (run_name + ' Please specific a legal numerical value for the maximum amount of threads')
	#test if the in-silico PCR server is ready
	elif not test_server(gfServer, servername, serverport):
		if remote_server == '':
			print (run_name + ' gfServer not ready, please start it')
		else:
			print (run_name + ' gfServer not ready, it is started now')
			if start_remote_server(servername) != '':
				print (run_name + ' Remote server was successfully started')
				parameters_legal = True
			else:
				print (run_name + ' Remote server could not be started')
	else:
		parameters_legal = True

	if parameters_legal == False:
		exit()

	#location of hg18.2bit
	pcr_location = gfPCR[0:len(gfPCR) - len('gfPCR') ]

	#############################################
	###passed all tests, now program can start###
	#############################################

	###multiprocess
	print (run_name + ' program started, please be patient')
	p = Pool(processes = max_threads)

	sequences = []

	fasta_file = open(fasta_filename, 'ru')
	for line in open(fasta_filename, 'ru'):
		if line.startswith('>'):
			sequences.append(line)
		else:
			sequences[-1] += line
	fasta_file.close()
	#print sequences
	results = p.map(get_primers, sequences)
	#results = get_primers(sequences[0])
	output = []
	stdoutput = []
	for a in results:
		output.append(a[0])
		stdoutput.append(a[1])
	final_output = open(data_dir + output_filename, 'w')
	final_output.write(''.join(output))
	final_output.close()

	print (''.join(stdoutput))

	print (run_name + ' done')
	sys.stdout = sys.__stdout__
	return ''.join(output)
if __name__ == "__main__":
	start_repeat_finder(True)


#Versions
#2015/2/1 V1.00 stable beta version
#2015/2/2 V1.01 fixed bug when no primers where found, added check for location of files and folders, moved import of parameters to a function, changed parameters to int or str, removed unused lines
#2015/2/25 V1.02 changed line feed to work on Linux and Windows
#2015/2/25 V1.03 added nested flag
#2015/2/27 V1.10 rearranged program, get_primers now does most of the job, added OUTPUT flag for output filename, cleaned code [range(0, replace open with xxx as], parallized execution
#replaced range with xrange
#2015/3/15 V1.11 added check_fasta function, rearranged sequence reading loop, added temporary file flag

#2016/1/3 replaced "b.find(a) > -1" with "a in b"
#To do:
#Add similarity filter to nested=0
#remove temporary files
