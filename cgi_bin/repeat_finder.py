#!/usr/bin/env python

import sys
import os
import subprocess
import multiprocessing
import socket
import logging
import time
import urllib
import json
import random
import argparse
import nucleotide_tools as nt
from support_functions import create_clean_filename, read_aws_conf
from Primer import Primer
from GfServer import GfServer
from StreamToLogger import StreamToLogger


# Python2/3 compatibility
if sys.version_info < (3, 0):
    from __builtin__ import xrange as range
    import ConfigParser
    import urllib2
else:
    import configparser as ConfigParser


started_via_commandline = False


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename='python.log',
    filemode='a'
)




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
    parser.add_argument('--SHUTDOWN', type=int, default=-1,
                        help='Shuts the isPCR server down after ### minutes, e.g. -SHUTDOWN 50, the server will be shutdown 50 minutes after the first job was started')
    parser.add_argument('--REMOTESERVER', type=str,
                        help='Specifies the URL of a server which can run primer3 via a REST API')
    parser.add_argument('--WAITINGPERIOD', type=float, default=0.25,
                        help='Specifies the time in seconds between server ping when a remote server is started, default = 0.25')
    parser.add_argument('--TIMEOUT', type=int, default=120,
                        help='Specifies the time in seconds until a remote server start is declared unsuccessful, default = 120')
    parser.add_argument('--RUNNAME', type=str,
                        help='Specifies the name of the run, only used for identifying jobs on the remote server')
    parser.add_argument('-@', '--config_file', type=str, dest='config_filename',
                        help='Specifies a file which list the above mentioned arguments, arguments used with --ARGUMENT will overwrite the arguments in the file')
    return parser.parse_args(args)


def import_parameters(arguments):
    """
    Imports parameters from commandline and validates them

    :param arguments: argparse object
    :return: tuple(bool, str), (True if valid, False if invalid), message
    """

    args = parse_args(arguments)
    if args.config_filename is not None:
        config_args = read_configfile(args.config_filename)
        for arg, value in config_args.items():
            args.__setattr__(arg, value)
    # TODO validate import parameters
    return True, ''


def create_primer3_file(seq_name, sequence, target, exclude, primer,
                        primer3_directory='.', standard_primer_settings_filename=None):
    """
    creates the input file for primer3
    if primerF and primerR are given, primerR is kept fixed and primerF is excluded, useful for nested PCR
    """
    if len(target) >= len(sequence):
        raise ValueError('target is longer than sequence')
    if target not in sequence:
        raise ValueError('target is not in sequence')

    new_filename = 'primer3_{}.txt'.format(create_clean_filename(seq_name))
    with open(os.path.join(primer3_directory, new_filename), 'w') as primer3_file:
        primer3_file.write('SEQUENCE_ID={}\n'.format(seq_name))
        primer3_file.write('SEQUENCE_TEMPLATE={}\n'.format(sequence))
        primer3_file.write('SEQUENCE_TARGET={},{}\n'.format(sequence.find(target) + 1, len(target)))
        primer3_file.write('SEQUENCE_EXCLUDED_REGION=')
        excluded_region = '{},{}\n'.format(sequence.find(target) + 1, len(target))
        if exclude is not None:
            for excluded_seq in exclude:
                excluded_region += 'SEQUENCE_EXCLUDED_REGION={},{}\n'.format(sequence.find(excluded_seq) + 1,
                                                                             len(excluded_seq))
        primer3_file.write(excluded_region)
        if primer.forward != '':
            primer3_file.write('SEQUENCE_EXCLUDED_REGION={},{}\n'.format(int(sequence.find(primer.forward) + len(primer.forward) / 3),
                                                                         int(len(primer.forward) / 3)))
        if primer.reverse != '':
            primer_r_reverse_comp = nt.reverse_complement(primer.reverse)
            right_end = sequence.find(primer_r_reverse_comp)
            primer3_file.write('SEQUENCE_FORCE_RIGHT_END={}\n'.format(right_end))
            primer3_file.write('SEQUENCE_FORCE_RIGHT_START={}\n'.format(right_end + len(primer_r_reverse_comp) - 1))

        if standard_primer_settings_filename is None:
            return

        with open(standard_primer_settings_filename, 'ru') as standard_primer3_file:
            for line in standard_primer3_file.readlines():
                primer3_file.write(line)


def check_specificity(primer, targetSequence, isPCRoutput):
    """
    takes a primer pair, a input sequence for which the primers were designed and checks in the isPCRoutput if the target sequence is amplified or something else
    also checks if the number of amplicons is exactly one
    return:
        True: if primerF and primerR are in targetSequence and only amplicon is amplified
        False: if any of the above criteria are not met
    """

    # checks if only one is amplicon created, if yes, continue, otherwise break the function
    if nt.count_amplicons(isPCRoutput, primer) != 1:
        return False

    found = False
    isPCRamplicon = ''
    temp_output = isPCRoutput.splitlines(True)
    i = 0

    while i < len(temp_output):
        line = temp_output[i]
        if not found and isPCRamplicon == '':
            if ' {} {}\n'.format(primer.forward, primer.reverse) in line and line.startswith('>'):
                found = True
        elif found and (not line.startswith('>') and line.find(';') == -1):
            isPCRamplicon += line
        elif line.startswith('>') or ';' in line and found:
            i = len(temp_output)
        i += 1

    if isPCRamplicon == '':
        return False

    isPCRamplicon = isPCRamplicon.replace('\n', '')
    isPCRamplicon = isPCRamplicon[len(primer.forward):]
    isPCRamplicon = isPCRamplicon[:len(isPCRamplicon) - len(primer.reverse)]

    return isPCRamplicon.upper() in targetSequence.upper()


def get_amplicon_from_primer3output(primer, primer3output):
    """
    takes primer3output and returns the amplicon based on primerF and primerR bindingsites and input sequence
    returns the amplicon without the primers
    """

    orig_output = primer3output
    amplicon_start = 0
    amplicon_end = -1
    sequence = ''

    while amplicon_start == 0 and '_SEQUENCE={}'.format(primer.forward) in primer3output:
        primer3output = primer3output[primer3output.find('_SEQUENCE={}'.format(primer.forward)):]
        primer3output = primer3output[primer3output.find('\n') - 1:]
        if primer3output[0:primer3output.find(primer.reverse)].count('\n') == 1:
            primer3output = primer3output[primer3output.find('PRIMER_LEFT_'):]
            primer3output = primer3output[primer3output.find('=') + 1:]
            amplicon_start = int(primer3output[0:primer3output.find(',')])
            primer3output = primer3output[primer3output.find('PRIMER_RIGHT_'):]
            primer3output = primer3output[primer3output.find('=') + 1:]
            amplicon_end = int(primer3output[0:primer3output.find(',')]) - len(primer.reverse)
        else:
            primer3output = primer3output[primer3output.find(primer.forward):]
            primer3output = '_SEQUENCE={}'.format(primer3output)

    end_line = 0
    primerF_found = False
    for i, line in enumerate(orig_output.split('\n')):
        if end_line == 0:
            if line.startswith('SEQUENCE_TEMPLATE='):
                sequence = line[len('SEQUENCE_TEMPLATE=') + 1:]
            elif line.startswith('PRIMER_LEFT_') and '_SEQUENCE={}'.format(primer.forward) in line and sequence != '':
                primerF_found = True

            if primerF_found:
                if line.startswith('PRIMER_RIGHT_') and '_SEQUENCE={}'.format(primer.reverse) in line:
                    end_line = i
            #TODO impossible to reach that piece of code!!!
            elif primerF_found and line.startswith('PRIMER_RIGHT_') and line.find('_SEQUENCE={}'.format(primer.reverse)) <= 0:
                primerF_found = False
    if amplicon_start != 0 and amplicon_end != -1:
        return sequence[amplicon_start - 1 + len(primer.forward):amplicon_end]

    return ''


def primer_stats(primer, primer3output):
    """
    takes a primer pair and primer3output as input
    returns GC-content, primer TM, product size, product TM
    input:
        primerF, primerR: string
        primer3output: string
    output:
        GC-content, primer TM, product size, product TM
    """

    temp_output = primer3output.splitlines()
    found = -1

    for i in range(len(temp_output)):
        if found == -1 and i < len(temp_output) - 1:
            if not temp_output[i].startswith('PRIMER_LEFT_'):
                continue
            if '_SEQUENCE=' not in temp_output[i] and not temp_output[i].endswith('={}'.format(primer.forward)):
                continue
            if not temp_output[i + 1].startswith('PRIMER_RIGHT_') and '_SEQUENCE=' not in temp_output[i + 1]:
                continue
            if temp_output[i + 1].endswith('={}'.format(primer.reverse)):
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

    if found == -1:
        raise RuntimeError('Primer not found in output')
    return '%.2f' % float(primerF_TM), '%.2f' % float(primerR_TM), '%.2f' % float(primerF_GC), '%.2f' % float(
        primerR_GC), '%.2f' % float(product_TM)



def make_output(primer, amplicon, isPCRoutput, primer3_output):
    """
    takes primers, amplicon, isPCR output and primer3 output as input
    generates output which can be written to log file
    """
    output = 'Primer pair:, {}, {}\n'.format(primer.forward, primer.reverse)
    output += 'Amplicon:, {}, {}{}{}\n{}\n'.format(isPCRoutput[isPCRoutput.find('\n') + 2:isPCRoutput.find('bp ') + 2].replace(' ', ', '),
                                                   primer.forward,
                                                   amplicon.lower(),
                                                   nt.reverse_complement(primer.reverse),
                                                   'primerF TM, primerR TM, primerF GC, primerR GC, product TM, product GC')

    amplicon_gc_content = nt.calculate_gc_content(primer.reverse + amplicon + primer.forward)
    output += ', '.join(primer_stats(primer, primer3_output)) + ', {}\n'.format(amplicon_gc_content)

    return output


def start_remote_server(*arguments):
    """
    Starts a remote AWS instance where primer3 and gfServer run
    Returns the remote server URL if the server was started successfully
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



def start_repeat_finder(started_via_commandline, *arguments):
    ###########################
    ###########################
    ###program starts here#####
    ###########################
    ###########################

    # Step 1: checks whether all input files and folders exist, and if the parameters are legal values

    max_similarity = 0.5
    fasta_filename = ''
    standard_primer_settings_filename = ''
    primer3_directory = ''
    primer3_exe = ''
    servername = ''
    serverport = - 1
    gfServer = ''
    gfPCR = ''
    max_repeats = -1
    max_primerpairs = -1
    nested = 0
    output_filename = 'batchprimer_output.txt'
    remove_temp_files = False
    hostname = ''
    compute_host = ''
    run_name = ''
    timeout = 120
    # redirects output if not started via commandline
    if started_via_commandline:
        import_parameters(sys.argv[1:])
    else:
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl

        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
        import_parameters(arguments)

    #############################################
    ###passed all tests, now program can start###
    #############################################

    ###multiprocess
    print('{} program started, please be patient'.format(run_name))

    sequences = []

    with open(fasta_filename, 'ru') as fasta_file:
        for line in fasta_file:
            if line.startswith('>'):
                sequences.append(line)
            else:
                sequences[-1] += line

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
    with open(os.path.join(data_dir, output_filename), 'w') as final_output:
        final_output.write(''.join(output))

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
