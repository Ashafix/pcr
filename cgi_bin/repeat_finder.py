#!/usr/bin/env python

import sys
import os
import ast
import subprocess
import multiprocessing
import socket
import logging
import time
import urllib
import json
import random
import argparse
from nucleotide_tools import similarity
from support_functions import create_clean_filename


# Python2/3 compatibility
if sys.version_info < (3, 0):
    from __builtin__ import xrange as range
    import ConfigParser
    import urllib2
else:
    import configparser as ConfigParser

with open('ssr_list.txt', 'r') as f:
    ssr_list = ast.literal_eval(f.read())

started_via_commandline = False


# http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
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
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename='python.log',
    filemode='a'
)


def read_configfile(config_filename):
    """
    reads the config file with all global entries
    """
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
                print('getConfig: unknown conf entry: ' + option)

    if standard_primer_settings_filename == '' or \
            primer3_directory == '' or \
            (primer3_exe == '' and remote_server == '') or \
            servername == '' or \
            serverport == '' or \
            gfServer == '' or \
            gfPCR == '' or \
            data_dir == '' or \
            max_threads < 1:
        print('getConfig: Missing entry')
        return {}
    else:
        return {'PRIMER3_SETTINGS': standard_primer_settings_filename,
                'PRIMER3_DIRECTORY': primer3_directory,
                'PRIMER3_EXE': primer3_exe,
                'SERVERNAME': servername,
                'SERVERPORT': serverport,
                'GFSERVER': gfServer,
                'GFPCR': gfPCR,
                'DATADIR': data_dir,
                'MAXTHREADS': max_threads}

def parse_args(args):
    parser = argparse.ArgumentParser(description='Hemi-NestR')
    parser.add_argument('--FASTA', type=str,
                        help='Specifies filename of fasta for which repeats and appropriate primers will be searched, e.g. -FASTA BRCA_markers.fa')
    parser.add_argument('--PRIMER3_SETTINGS', type=str,
                        help='Specifies filename which specifies the settings which are used for searching primers, e.g. -PRIMER3_SETTINGS BRCA_markers_primers.txt')
    parser.add_argument('--PRIMER3_DIRECTORY', type=str,
                        help='Specifies a directory where the output files will be saved, e.g. PRIMER3_DIRECTORY /home/user/pcr/BRCA_markers/')
    parser.add_argument('--PRIMER3_EXE', type=str,
                        help='Specifies the location of the primer3_core executable, e.g. --PRIMER3_EXE /home/pcr/bin/x86_64/primer3_core')
    parser.add_argument('--SERVERNAME', type=str,
                        help='Specifies the name of the isPCR server (usually name of the computer running isPCR), e.g. --SERVERNAME pcrcomputer')
    parser.add_argument('--SERVERPORT', type=int,
                        help='Specifies the port which is used to communicate with the isPCR server, e.g. --SERVERPORT 33334')
    parser.add_argument('--MAXREPEATS', type=int,
                        help='Specifies the maximum length of repeats to search, e.g. --MAXREPEATS 3, searches for repeats of di- and trinucleotides')
    parser.add_argument('--PRIMERPAIRS', type=str,
                        help='Specifies the number of suitable primer pairs which will be returned')
    parser.add_argument('--GFSERVER', type=str,
                        help='Specifies the location of the gfServer executable')
    parser.add_argument('--GFPCR', type=str,
                        help='Specifies the location of the gfPCR executable')
    parser.add_argument('--MAX_SIMILARITY', type=str,
                        help='Specifies the maximal similarity for two primer pairs in order to be accepted, from 0 to 1, default = 0.5')
    parser.add_argument('--NESTED', type=int, default=1,
                        help='Specifies whether the program should search for nested primers if not enough pairs have been found (0), never search (-1) or always search for primers (1)')
    parser.add_argument('--OUTPUT', type=str,
                        help='Specifies the output filename where all the primers and target will be saved, default: batchprimer_output.txt')
    parser.add_argument('--MAXTHREADS', type=int,
                        help='Specifies how many threads are started in parallel, should be less than your number of CPU cores')
    parser.add_argument('--REMOVETEMPFILES', type=bool, default=False,
                        help='Specifies whether temporary files (e.g. Primer3 input and output) will be deleted after the program finishes. Default is False')
    parser.add_argument('--SHUTDOWN', type=bool, default=-1,
                        help='Shuts the isPCR server down after ### minutes, e.g. -SHUTDOWN 50, the server will be shutdown 50 minutes after the first job was started')
    parser.add_argument('--REMOTESERVER', type=str,
                        help='Specifies the URL of a server which can run primer3 via a REST API')
    parser.add_argument('--WAITINGPERIOD', type=float, default=0.25,
                        help='Specifies the time in seconds between server ping when a remote server is started, default = 0.25')
    parser.add_argument('--TIMEOUT', type=int, default=120,
                        help='Specifies the time in seconds until a remote server start is declared unsuccessful, default = 120')
    parser.add_argument('--RUNNAME', type=str,
                        help='Specifies the name of the run, only used for identifying jobs on the remote server')
    parser.add_argument('-@', '--config_file', type=str,
                        help='Specifies a file which list the above mentioned arguments, arguments used with -ARGUMENT will overwrite the arguments in the file')
    return parser.parse_args(args)



def test_server(gfserver, servername, serverport):
    """
    tests the gfServer and returns True if the server is working

    :param gfserver:
    :param servername:
    :param serverport:
    :return: bool, True if the server is responding correctly, False, if the server does not responds or the response is incorrect
    """

    command_line = '{} status {} {}'.format(gfserver, servername, serverport)

    try:
        gfserver_response = subprocess.check_output([command_line], shell=True, stderr=subprocess.STDOUT)
    except:
        return False

    if gfserver_response.startswith('Couldn'):
        return False
    return 'version' in gfserver_response and 'port' in gfserver_response and 'host' in gfserver_response and 'type' in gfserver_response


def count_amplicons(isPCRoutput, primerF, primerR):
    """
    Takes a list of isPCRoutputs and counts the numbers of amplicons for a primer pair
    """
    startpoint = isPCRoutput.find('{};{}\n'.format(primerF, primerR))
    if startpoint == -1:
        return -1
    if startpoint > 0:
        if isPCRoutput[startpoint - 1:startpoint] != '\n':
            return -1

    isPCRfragment = isPCRoutput[startpoint:]
    if isPCRfragment.find(';', len(primerF) + len(primerR) + 2) > -1:
        isPCRfragment = isPCRfragment[0:isPCRfragment.find(';', len(primerF) + len(primerR) + 2)]

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
            for i in range(1, int(round(len(sequence) / 2, 0))):
                if ssr * i in sequence and i * len(ssr) >= 9:
                    max_length = i
            if max_length > 0:
                to_exclude.append(ssr * max_length)
    return to_exclude


def import_parameters(*arguments):
    """
    imports parameters from commandline
    """

    data_dir = './'
    input_args = []
    if len(sys.argv) > 1 or len(arguments) == 0:
        if str(sys.argv).find('-help') > -1:
            print_help()
            sys.exit()
        else:
            input_args = sys.argv
    if not started_via_commandline and len(arguments) > 0:
        for argument in arguments[0][0]:
            input_args.append(argument)

    # reads config file
    for i in range(len(input_args)):
        if str(input_args[i]).startswith('-@'):
            read_configfile(input_args[i + 1])

    # reads named arguments
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
        elif str(input_args[i]).upper() == '-GFSERVER':
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
    if (fasta_filename == '' or standard_primer_settings_filename == '' or
            primer3_directory == '' or
            primer3_exe == '' or
            servername == '' or
            serverport == -1 or
            max_repeats == -1 or
            gfServer == '' or
            gfPCR == '' or
            abs(nested) > 1):
        print('Input arguments')
        print('fasta_filename: ' + fasta_filename)
        print('standard_primer_settings_filename: ' + standard_primer_settings_filename)
        print('primer3_directory: ' + primer3_directory)
        print('primer3_exe: ' + primer3_exe)
        print('servername: ' + servername)
        print('serverport: ' + str(serverport))
        print('max_repeats: ' + str(max_repeats))
        print('gfServer: ' + gfServer)
        print('gfPCR: ' + gfPCR)
        print('nested: ' + str(nested))
        print('Missing arguments!\n\n')
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
    if len(target) >= len(sequence) or target not in sequence:
        return False

    new_filename = 'primer3_{}.txt'.format(create_clean_filename(seq_name))
    with open(os.path.join(primer3_directory, new_filename), 'w') as primer3_file:
        primer3_file.write('SEQUENCE_ID=')
        primer3_file.write(seq_name + '\n')
        primer3_file.write('SEQUENCE_TEMPLATE=')
        primer3_file.write(sequence + '\n')
        primer3_file.write('SEQUENCE_TARGET=')
        primer3_file.write(str(sequence.find(target) + 1))
        primer3_file.write(',')
        primer3_file.write(str(len(target)) + '\n')
        primer3_file.write('SEQUENCE_EXCLUDED_REGION=')
        excluded_region = '{},{}\n'.format(sequence.find(target) + 1, len(target))
        if exclude is not None:
            for excluded_seq in exclude:
                excluded_region += 'SEQUENCE_EXCLUDED_REGION={},{}\n'.format(sequence.find(excluded_seq) + 1,
                                                                             len(excluded_seq))
        primer3_file.write(excluded_region)
        if primerF != '' and primerR != '':
            primer3_file.write('SEQUENCE_EXCLUDED_REGION={},{}\n'.format(int(sequence.find(primerF) + len(primerF) / 3),
                                                                         int(len(primerF) / 3)))
            primerR = primerR.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
            primer3_file.write('SEQUENCE_FORCE_RIGHT_END={}\n'.format(sequence.find(primerR))
            primer3_file.write('SEQUENCE_FORCE_RIGHT_START={}\n'.format(sequence.find(primerR) + len(primerR) - 1))

        with open(standard_primer_settings_filename, 'ru') as standard_primer3_file:
            for line in standard_primer3_file.readlines():
                primer3_file.write(line)

    return True




def check_specificity(primerF, primerR, targetSequence, isPCRoutput):
    """
    takes a primer pair, a input sequence for which the primers were designed and checks in the isPCRoutput if the target sequence is amplified or something else
    also checks if the number of amplicons is exactly one
    return:
        True: if primerF and primerR are in targetSequence and only amplicon is amplified
        False: if any of the above criteria are not met
    """

    # checks if only one is amplicon created, if yes, continue, otherwise break the function
    if count_amplicons(isPCRoutput, primerF, primerR) != 1:
        return False

    found = False
    isPCRamplicon = ''
    temp_output = isPCRoutput.splitlines(True)
    i = 0

    while i < len(temp_output):
        line = temp_output[i]
        if not found and isPCRamplicon == '':
            if ' {} {}\n'.format(primerF, primerR) in line and line.startswith('>'):
                found = True
        elif found and (not line.startswith('>') and line.find(';') == -1):
            isPCRamplicon += line
        elif line.startswith('>') or ';' in line and found:
            i = len(temp_output)
        i += 1

    if isPCRamplicon == '':
        return False

    isPCRamplicon = isPCRamplicon.replace('\n', '')
    isPCRamplicon = isPCRamplicon[len(primerF):]
    isPCRamplicon = isPCRamplicon[:len(isPCRamplicon) - len(primerR)]

    return isPCRamplicon.upper() in targetSequence.upper()


def get_amplicon_from_primer3output(primerF, primerR, primer3output):
    """
    takes primer3output and returns the amplicon based on primerF and primerR bindingsites and input sequence
    returns the amplicon without the primers
    """
    primerF = primerF.upper()
    primerR = primerR.upper()
    # check validity of input
    if not primerF or not primerR:
        return ''
    nucleotides = set('ATGC')
    if not set(primerF).issubset(nucleotides) or not set(primerR).issubset(nucleotides):
        return ''
    amplicon_start = 0
    primerF_found = False
    sequence = ''
    end_line = 0
    orig_output = primer3output
    amplicon_end = -1

    while amplicon_start == 0 and '_SEQUENCE={}'.format(primerF) in primer3output:
        primer3output = primer3output[primer3output.find('_SEQUENCE={}'.format(primerF)):]
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
            primer3output = '_SEQUENCE={}'.format(primer3output)

    for i, line in enumerate(orig_output.split('\n')):
        if end_line == 0:
            if line.startswith('SEQUENCE_TEMPLATE='):
                sequence = line[len('SEQUENCE_TEMPLATE=') + 1:]
            elif line.startswith('PRIMER_LEFT_') and '_SEQUENCE={}'.format(primerF) in line and sequence != '':
                primerF_found = True

            if primerF_found:
                if line.startswith('PRIMER_RIGHT_') and '_SEQUENCE={}'.format(primerR) in line:
                    end_line = i
            elif primerF_found and line.startswith('PRIMER_RIGHT_') and line.find('_SEQUENCE={}'.format(primerR)) <= 0:
                primerF_found = False
    if amplicon_start != 0 and amplicon_end != -1:
        return sequence[amplicon_start - 1 + len(primerF):amplicon_end]

    return ''


def primer_stats(primerF, primerR, primer3output):
    """
    takes a primer pair and primer3output as input
    returns GC-content, primer TM, product size, product TM
    input:
        primerF, primerR: string
        primer3output: string
    output:
        GC-content, primer TM, product size, product TM
    """
    primerF = primerF.upper()
    primerR = primerR.upper()
    temp_output = primer3output.splitlines()
    found = -1

    for i in range(len(temp_output)):
        if found == -1 and i < len(temp_output) - 1:
            if not temp_output[i].startswith('PRIMER_LEFT_'):
                continue
            if not '_SEQUENCE=' in temp_output[i] and not temp_output[i].endswith('={}'.format(primerF)):
                continue
            if not temp_output[i + 1].startswith('PRIMER_RIGHT_') and not '_SEQUENCE=' in temp_output[i + 1]:
                continue
            if temp_output[i + 1].endswith('={}'.format(primerR)):
                found = temp_output[i][len('PRIMER_LEFT_'):temp_output[i].find('_SEQUENCE')]
        else:
            if temp_output[i].startswith('PRIMER_LEFT_{}_TM='.format(found)):
                primerF_TM = temp_output[i][temp_output[i].find('=') + 1:]
            elif temp_output[i].startswith('PRIMER_RIGHT_{}_TM='.format(found)):
                primerR_TM = temp_output[i][temp_output[i].find('=') + 1:]
            elif temp_output[i].startswith('PRIMER_LEFT_{}_GC_PERCENT='.format(found)):
                primerF_GC = temp_output[i][temp_output[i].find('=') + 1:]
            elif temp_output[i].startswith('PRIMER_RIGHT_{}_GC_PERCENT='.format(found)):
                primerR_GC = temp_output[i][temp_output[i].find('=') + 1:]
            elif temp_output[i].startswith('PRIMER_PAIR_{}_PRODUCT_TM='.format(found)):
                product_TM = temp_output[i][temp_output[i].find('=') + 1:]

    if found != -1:
        return '%.2f' % float(primerF_TM), '%.2f' % float(primerR_TM), '%.2f' % float(primerF_GC), '%.2f' % float(
            primerR_GC), '%.2f' % float(product_TM)
    else:
        print(run_name + ' Error: Primer not found in output')
        return '0', '0', '0', '0', '0'


def make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output):
    """
    takes primers, amplicon, isPCR output and primer3 output as input
    generates output which can be written to log file
    """
    output = 'Primer pair:, {}, {}{sep}'.format(primerF, primerR, sep=os.linesep)
    output += 'Amplicon:, {}, {}{}{}\n{}'.format(isPCRoutput[isPCRoutput.find('\n') + 2:isPCRoutput.find('bp ') + 2].replace(' ',
                                                                                                          ', '),
                                                 primerF.upper(),
                                                 amplicon.lower(),
                                                 reverse_complement(primerR),
                                                 'primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC\n')

    ampliconGC = str(round(100 * (float(str(primerF + amplicon + primerR).count('G')) + float(
        str(primerF + amplicon + primerR).count('C'))) / float(len(str(primerF + amplicon + primerR))), 2))
    output += ', '.join(primer_stats(primerF, primerR, primer3_output)) + ', ' + ampliconGC + '\n'

    return output


def check_fasta(sequence, fasta_type, strict):
    """
    checks if an input sequence looks like a proper single fasta sequence
    sequence: string the input sequence
    fasta_type: protein or nucleotide
    strict: boolean, enforces perfect format, i.e. no extra line breaks or spaces, etc.
    """

    fasta_type = fasta_type.upper()

    if fasta_type == 'PROTEIN' or \
            fasta_type.startswith('P') or \
            fasta_type == 'AA' or \
            fasta_type.startswith('AMINOACID') or \
            fasta_type.startswith('AMINO ACID'):
        if strict:
            allowed_characters = 'ARNDCEQGHILKMFPSTWYV'
        else:
            allowed_characters = 'ARNDBCEQZGHILKMFPSTWYV'
    elif fasta_type.startswith('NUC') or \
            fasta_type == 'DNA' or \
            fasta_type == 'N' or \
            fasta_type == 'BASES':
        if strict:
            allowed_characters = 'ATGC'
            allowed_characters += allowed_characters.lower()
        else:
            allowed_characters = 'ATGCURYSWKMBDHVN.-'
    else:
        allowed_characters = ''

    if not strict:
        sequence = sequence.strip()

    # checks if header is present
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
            else:
                if len(lines) != 2:
                    sequence = ''
                else:
                    sequence = lines[1]
            if len(sequence) > 0:
                passed = all(i in allowed_characters for i in sequence)
            else:
                passed = False
    return passed


def get_primers(sequence):
    """
    main function
    finds primers for a given sequence
    """
    global max_primerpairs
    global nested
    global run_name
    # creates primer3 input file for each sequence
    output = ''
    stdoutput = ''
    sequences = [sequence.split('\n', 1)[0][1:],
                 ''.join(sequence.split('\n', 1)[1:]).replace('\n', '')]

    if not check_fasta('>{}'.format('\n'.join(sequences)), 'NUCLEOTIDE', False):
        stdoutput += 'Sequence did not match FASTA format, no primers were designed\n'
        output = stdoutput
        return output, stdoutput

    create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats), exclude_list(sequences[1]),
                        '', '')

    stdoutput += 'Primer3 will be started now, please be patient\n'

    primer3_output = ''
    filename = 'primer3_{}.txt'.format(create_clean_filename(sequences[0]))
    primer3_input = ''

    with open(primer3_directory + filename, 'ru') as temp_file:
        primer3_input += ''.join(temp_file.readlines())
    temp_file.close()

    stdoutput += 'Primer3 subprocess started\n'
    if remote_server != '':
        local_run_name = '{}_{}'.format(run_name, os.getpid())
        primer3_output, comment = execute_primer3(primer3_input, local_run_name)
        stdoutput += comment
    else:
        sys.stdout = open(str(os.getpid()) + ".out", "w")
        process = subprocess.Popen(primer3_exe,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.stdin.write(primer3_input)
        primer3_output += process.communicate()[0] + '\n'
    stdoutput += 'Primer3 finished\n'
    primer3_list = []

    for lines in primer3_output.split('\n'):
        if lines.startswith('SEQUENCE_ID'):
            primer3_list.append(lines)
        elif lines.find('SEQUENCE=') > 0:
            if lines.startswith('PRIMER_LEFT') or lines.startswith('PRIMER_RIGHT'):
                primer3_list.append(lines[lines.find('=') + 1:])
    print(run_name + " ##################")

    isPCRoutput = ''


    # list of primers which only amplify one amplicon
    accepted_primers = []

    # list of primers which can be used to search for nested primers
    accepted_nested_templates = []


    # Step 4: checks all created primers
    output += '==========\nTarget:, {}\n\n'.format(primer3_list[0][primer3_list[0].find('=') + 1:])
    primerF_1st = ''
    primerR_1st = ''

    for i in range(1, len(primer3_list), 2):
        if len(accepted_primers) < max_primerpairs:
            primerF = primer3_list[i]
            primerR = primer3_list[i + 1]
            # checks if the primers do not contain repeats, e.g. GAGAGA, not longer than 2x2 repeat
            # if not, runs isPCR to see if they are specific
            if dinucleotide_repeat(primerF) >= 6 or dinucleotide_repeat(primerR) >= 6:
                no_amplicons = 0
                stdoutput += '{} {} rejected, repeats\n'.format(primerF, primerR)
            else:
                process = subprocess.Popen(
                    [gfPCR, servername, str(serverport), pcr_location, primerF, primerR, 'stdout'],
                    stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                isPCRoutput = '{};{}\n{}'.format(primerF, primerR, process.communicate()[0])
                no_amplicons = count_amplicons(isPCRoutput, primerF, primerR)

            i += 1

            # checks if the primer pair amplifies only one amplicon
            if no_amplicons == 1:
                amplicon = get_amplicon_from_primer3output(primerF, primerR, primer3_output)

                # checks if the primer pair amplifies the original target sequence
                accept_primerpair = False
                # should be checked against all primers, not only the first pair
                if check_specificity(primerF, primerR, amplicon, isPCRoutput):
                    if len(accepted_primers) == 0:
                        primerF_1st = primerF
                        primerR_1st = primerR
                        accept_primerpair = True
                    elif similarity(primerF, primerF_1st) < max_similarity and similarity(primerR,
                                                                                          primerR_1st) < max_similarity:
                        accept_primerpair = True

                    # if the pair is accepted it will be written to the output file
                    if accept_primerpair and nested != 1:
                        accepted_primers.append('{},{}'.format(primerF, primerR))
                        output += make_output(primerF, primerR, amplicon, isPCRoutput, primer3_output)
                        stdoutput += output + '\n'
                    # v1.03
                    elif accept_primerpair and nested == 1:
                        accepted_nested_templates.append('{},{}'.format(primerF, primerR))
            else:
                stdoutput += '{} {} rejected, not exactly one amplicon\n'.format(primerF, primerR)
            # checks if not enough suitable primer pairs have been found
            # then tries to design primers for nested PCR
            # if yes, tries to redesign primers with identical reverse primer but different forward primer

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

            elif len(accepted_primers) != 0 and \
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
                primerF_nested = ''
                # creates new primer3 file with fixed reverse primer
                create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats),
                                    exclude_list(sequences[0]), primerF_1st, primerR_1st)
                filename = 'primer3_{}.txt'.format(create_clean_filename(sequences[0]))
                with open(primer3_directory + filename, 'ru') as temp_file:
                    primer3_input = ''.join(temp_file.readlines())
                if remote_server != '':
                    execute_primer3(primer3_input, local_run_name)
                else:
                    process = subprocess.Popen(primer3_exe, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                    process.stdin.write(primer3_input)
                    primer3_nested_output += process.communicate()[0] + '\n'
                stdoutput += 'Primer3 for nested primers finished\n'
                for lines in primer3_nested_output.split('\n'):
                    if lines.find('SEQUENCE') > 0:
                        if lines.startswith('PRIMER_LEFT'):
                            primerF_nested = lines[lines.find('=') + 1:]
                        elif lines.startswith('PRIMER_RIGHT'):
                            primerR_nested = lines[lines.find('=') + 1:]
                            # checks if the new, nested primer pair is specific
                            amplicon = get_amplicon_from_primer3output(primerF_nested, primerR_nested,
                                                                       primer3_nested_output)

                            if dinucleotide_repeat(primerF_nested) >= 6 or \
                                    dinucleotide_repeat(primerR_nested) >= 6:
                                stdoutput += '{} {} rejected, repeats\n'.format(primerF_nested,primerR_nested)
                            else:
                                process = subprocess.Popen(
                                    [gfPCR, servername, str(serverport), pcr_location, primerF_nested, primerR_nested,
                                     'stdout'],
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
                                isPCRoutput_nested = '{};{}\n{}'.format(primerF_nested,
                                                                        primerR_nested,
                                                                        process.communicate()[0])

                                if check_specificity(primerF_nested, primerR_nested, amplicon, isPCRoutput_nested):
                                    if similarity(primerF_nested, primerF_1st) < max_similarity:
                                        stdoutput += '{} {} found nested primer\n'.format(primerF_nested,
                                                                                          primerR_nested)
                                        accepted_primers.append('{},{}'.format(primerF_nested,
                                                                               primerR_nested))
                                        output += make_output(primerF_nested, primerR_nested, amplicon,
                                                              isPCRoutput_nested, primer3_nested_output)
                                        stdoutput += output + '\n'
                                        break
                                    else:
                                        stdoutput += '{} {} too similar\n'.format(primerF_nested,
                                                                                  primerR_nested)
                                else:
                                    stdoutput += '{} {} not specific\n'.format(primerF_nested, primerR_nested)

                if len(accepted_primers) < max_primerpairs:
                    stdoutput += 'Not enough primer pairs could be found\n'
                    max_primerpairs = 0
            ####
            # added in v1.03 for forced nested primers
            elif nested == 1 and (i + 1 >= len(primer3_list) or (i != 0 and primer3_list[i + 1].startswith('SEQUENCE_ID'))) and len(accepted_nested_templates) > 0:
                stdoutput += 'forced to trying to find nested primers\n'
                # creates new primer3 file with fixed reverse primer
                for accepted_nested_template in accepted_nested_templates:
                    if len(accepted_primers) < max_primerpairs:
                        primerF_1st = accepted_nested_template[0:accepted_nested_template.find(',')]
                        primerR_1st = accepted_nested_template[accepted_nested_template.find(',') + 1:]
                        create_primer3_file(sequences[0], sequences[1], find_repeats(sequences[1], max_repeats),
                                            exclude_list(sequences[0]), primerF_1st, primerR_1st)
                        filename = 'primer3_{}.txt'.format(create_clean_filename(sequences[0]))
                        primer3_input = ''
                        with open(primer3_directory + filename, 'ru') as temp_file:
                            primer3_input += ''.join(temp_file.readlines())

                        primer3_nested_output, comment = execute_primer3(primer3_input,
                                                                         '{}nested{}'.format(filename,
                                                                                             random.random()))
                        stdoutput += comment
                        primer3_nested_output += primer3_nested_output + '\n'
                        primerF_nested = ''

                        for lines in primer3_nested_output.split('\n'):
                            if lines.find('SEQUENCE') > 0:
                                if lines.startswith('PRIMER_LEFT'):
                                    primerF_nested = lines[lines.find('=') + 1:]

                                elif lines.startswith('PRIMER_RIGHT'):
                                    primerR_nested = lines[lines.find('=') + 1:]
                                    # checks if the new, nested primer pair is specific
                                    amplicon = get_amplicon_from_primer3output(primerF_nested, primerR_nested,
                                                                               primer3_nested_output)

                                    if dinucleotide_repeat(primerF_nested) >= 6 or dinucleotide_repeat(
                                            primerR_nested) >= 6:
                                        stdoutput += '{} {} rejected, repeats\n'.format(primerF_nested,
                                                                                        primerR_nested)
                                    else:
                                        process = subprocess.Popen(
                                            [gfPCR, servername, str(serverport), pcr_location, primerF_nested,
                                             primerR_nested, 'stdout'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                                        isPCRoutput_nested = '{};{}\n{}'.format(primerF_nested,
                                                                                primerR_nested,
                                                                                process.communicate()[0])

                                        if check_specificity(primerF_nested, primerR_nested, amplicon,
                                                             isPCRoutput_nested):
                                            if similarity(primerF_nested, primerF_1st) < max_similarity:
                                                stdoutput += '{} {} found forced nested primer\n'.format(primerF_1st,
                                                                                                         primerR_nested)
                                                accepted_primers.append('{},{}'.format(primerF_1st,primerR_1st))
                                                accepted_primers.append('{},{}'.format(primerF_nested, primerR_nested))

                                                process = subprocess.Popen(
                                                    [gfPCR, servername, str(serverport), pcr_location, primerF_1st,
                                                     primerR_1st, 'stdout'], stdout=subprocess.PIPE,
                                                    stdin=subprocess.PIPE)
                                                isPCRoutput = '{};{}\n{}'.format(primerF_1st,
                                                                                 primerR_1st,
                                                                                 process.communicate()[0])
                                                amplicon = get_amplicon_from_primer3output(primerF_1st, primerR_1st,
                                                                                           primer3_output)
                                                output += make_output(primerF_1st, primerR_1st, amplicon, isPCRoutput,
                                                                      primer3_output)
                                                # should fix the problem with the doubled amplicon
                                                amplicon = get_amplicon_from_primer3output(primerF_nested,
                                                                                           primerR_nested,
                                                                                           primer3_nested_output)
                                                output += make_output(primerF_nested, primerR_nested, amplicon,
                                                                      isPCRoutput_nested, primer3_nested_output)
                                                stdoutput += output + '\n'
                                                break
                                            else:
                                                stdoutput += '{} {} too similar\n'.format(primerF_1st, primerR_nested)
                                        else:
                                            stdoutput += '{} {} not specific\n'.format(primerF_nested, primerR_nested)

                stdoutput += 'Primer3 for forced nested primers finished\n'

    if (len(accepted_primers) < max_primerpairs and nested == -1) or (len(accepted_primers) < 2 and nested != -1):
        stdoutput += 'not enough primer pairs found\n'

    with open(str(os.getpid()) + ".tmp", "w") as temp:
        temp.write(output)
        temp.write(stdoutput)

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

    try:
        import boto3
    except ImportError:
        sys.stderr.write('Python module boto3 could not be imported, if you are using AWS, please install it.\n')
        return ''

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
    print('Start remote server<br />')
    print('Server name: {}'.format(servername))
    print('<br />gfServer: {}'.format(gfServer))
    print('<br />Server port: {}'.format(serverport))
    print('<br />Time out: {}'.format(timeout))

    aws = read_aws_conf()
    session = boto3.session.Session(aws_access_key_id=aws['aws_access_key_id'],
                                    aws_secret_access_key=aws['aws_secret_access_key'],
                                    region_name=aws['region_name'])
    ec2 = session.resource('ec2')

    instances = ec2.instances.all()
    if len(list(instances)) < 2:
        print('No second AWS instance was found!')
        return ''

    hostname = socket.gethostbyaddr(socket.gethostname())[0]
    compute_host = ''
    for instance in instances:
        instance_name = ''
        if instance.private_dns_name != hostname and compute_host == '':
            # get the base hostname
            for tag in instance.tags:
                if 'Value' in tag:
                    if 'Key' in tag.keys() and 'Value' in tag.keys():
                        if tag['Key'] == 'Name':
                            # checks if the right instance type was selected
                            if server_extension in tag['Value']:
                                instance_name = tag['Value']
            if instance_name == servername + server_extension:
                servername = instance.private_dns_name
                print('<br /> Servername: {}<br />'.format(servername))
                compute_host = instance.id
                instance.start()
                # wait until the instance is up and running
                local_timeout = timeout
                while instance.state['Code'] != 16 and local_timeout > 0:
                    time.sleep(waiting_period)
                    local_timeout += -waiting_period
                if local_timeout < 0:
                    print('Server start was unsuccesful, the timeout period was exceeded')
                    return ''
                if not test_server(gfServer, servername, serverport):
                    print('Server start was successful, but gfServer does not respond')
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

    # Step 1: checks whether all input files and folders exist, and if the parameters are legal values
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
    serverport = - 1
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
    # redirects output if not started via commandline
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

    # all input parameters are valid
    parameters_legal = False

    if not os.path.isfile(fasta_filename):
        print(run_name + ' Fasta file could not be found')
        print(fasta_filename)
    elif not os.path.isfile(standard_primer_settings_filename):
        print(os.path.isfile(standard_primer_settings_filename))
        print(run_name + ' Primer3 settings file could not be found')
    elif not os.path.isfile(primer3_exe):
        print(run_name + ' Primer3.exe file could not be found')
        print(primer3_exe)
    elif not os.path.isfile(gfPCR):
        print(run_name + ' gfPCR.exe file could not be found')
        print(gfPCR)
    elif not os.path.isdir(primer3_directory):
        print(run_name + ' Primer3 directory does not exist')
        print(primer3_directory)
    elif serverport <= 0:
        print(run_name + ' Please specificy a legal numerical value for the server port')
    elif int(max_repeats) < 0:
        print(run_name + ' Please specificy a legal numerical value for the max repeats')
    elif max_primerpairs < 0:
        print(run_name + ' Please specificy a legal numerical value for the max primer pairs')
    elif max_threads < 1:
        print(run_name + ' Please specific a legal numerical value for the maximum amount of threads')
    # test if the in-silico PCR server is ready
    elif not test_server(gfServer, servername, serverport):
        if remote_server == '':
            print(run_name + ' gfServer not ready, please start it')
        else:
            print(run_name + ' gfServer not ready, it is started now')
            if start_remote_server(servername) != '':
                print(run_name + ' Remote server was successfully started')
                parameters_legal = True
            else:
                print(run_name + ' Remote server could not be started')
    else:
        parameters_legal = True

    if not parameters_legal:
        exit()

    # location of hg18.2bit
    pcr_location = gfPCR[0:len(gfPCR) - len('gfPCR')]

    #############################################
    ###passed all tests, now program can start###
    #############################################

    ###multiprocess
    print(run_name + ' program started, please be patient')

    sequences = []

    fasta_file = open(fasta_filename, 'ru')
    for line in open(fasta_filename, 'ru'):
        if line.startswith('>'):
            sequences.append(line)
        else:
            sequences[-1] += line
    fasta_file.close()
    if len(sequences) > 1:
        p = multiprocessing.Pool(processes=max_threads)
        results = p.map(get_primers, sequences)
        p.terminate()
    else:
        results = [get_primers(sequences[0])]

    output = []
    stdoutput = []
    for a in results:
        output.append(a[0])
        stdoutput.append(a[1])
    final_output = open(data_dir + output_filename, 'w')
    final_output.write(''.join(output))
    final_output.close()

    print(''.join(stdoutput))

    print(run_name + ' done')
    sys.stdout = sys.__stdout__
    return ''.join(output)


def execute_primer3(primer3_input, local_run_name, port=8003):
    baseurl = '{}:{}'.format(remote_server, port)
    params = urllib.urlencode({'run_name': local_run_name, 'primer3_input': primer3_input})
    primer3_request = urllib2.Request(baseurl + '/primer3', params)
    urllib2.urlopen(primer3_request)
    primer3_status = ''

    max_time = 1200
    waiting_period = 2
    while primer3_status != 'finished' and max_time > 0:
        time.sleep(waiting_period)
        max_time -= waiting_period
        params = urllib.urlencode({'run_name': local_run_name})
        primer3_url = urllib2.urlopen('{}/job_status?{}'.format(baseurl, params))
        primer3_response = primer3_url.read()
        if 'job_status' in primer3_response:
            try:
                primer3_status = json.loads(primer3_response)['job_status'][local_run_name]
            except:
                primer3_status = ''
    if max_time > 0:
        primer3_url = urllib2.urlopen('{}/job_results?'.format(baseurl, params))
        primer3_output = primer3_url.read()
        while '\\n' in primer3_output:
            primer3_output = primer3_output.replace('\\n', '\n')
        primer3_output = primer3_output[1:-1] + '\n'
    else:
        return '', 'Primer3 failed to generate output in max time\n'

    return primer3_output, ''


if __name__ == "__main__":
    start_repeat_finder(True)

# Versions
# 2015/2/1 V1.00 stable beta version
# 2015/2/2 V1.01 fixed bug when no primers where found, added check for location of files and folders, moved import of parameters to a function, changed parameters to int or str, removed unused lines
# 2015/2/25 V1.02 changed line feed to work on Linux and Windows
# 2015/2/25 V1.03 added nested flag
# 2015/2/27 V1.10 rearranged program, get_primers now does most of the job, added OUTPUT flag for output filename, cleaned code [range(0, replace open with xxx as], parallized execution
# replaced range with xrange
# 2015/3/15 V1.11 added check_fasta function, rearranged sequence reading loop, added temporary file flag

# 2016/1/3 replaced "b.find(a) > -1" with "a in b"
# To do:
# Add similarity filter to nested=0
# remove temporary files
