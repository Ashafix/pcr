#!/usr/bin/env python

import sys
import os
import multiprocessing
import logging
import argparse
from StreamToLogger import StreamToLogger
from RepeatFinder import RepeatFinder


# Python2/3 compatibility
if sys.version_info < (3, 0):
    import ConfigParser
else:
    import configparser as ConfigParser


started_via_commandline = False


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
    value_map = {'PRIMER3_SETTINGS': str,
                 'PRIMER3_DIRECTORY': str,
                 'SERVERNAME': str,
                 'SERVERPORT': str,
                 'GFSERVER': str,
                 'GFPCR': str,
                 'DATADIR': str,
                 'MAXTHREADS': int,
                 'WAITINGPERIOD': float,
                 'TIMEOUT': int,
                 'RUNNAME': str
                 }
    output = {}
    for section in config.sections():
        for option in config.options(section):
            _option = option.upper()
            if _option in value_map:
                output[_option] = value_map[_option](config.get(section, option).strip())
            else:
                raise ValueError('getConfig: unknown conf entry: {}'.format(option))

    return output


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





def get_primers(sequence):
    r = RepeatFinder()
    return r.get_primers(sequence)


def start_repeat_finder(started_via_commandline, max_threads=None, *arguments):
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

    if max_threads is None:
        max_threads = multiprocessing.cpu_count()

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
