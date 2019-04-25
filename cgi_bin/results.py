#!/usr/bin/env python

import sys
import os
import random
import cgi
import string
from shutil import copyfile
import urllib2
import urllib
import time
import ast
import boto3
import StringIO
from nucleotide_tools import clean_sequence
from constants_web import HEADER, END, SCRIPT, TABLE_ROW, NOT_PUBLIC, MAX_SEQUENCES, RESULTS, STATUS, SCRIPT_RESULTS

global data_dir
global run_name


def main():

    config_filename = 'batchprimer.conf'
    input_args = []
    cgi_args = ['batchname', 'maxrepeats', 'primerpairs', 'maxsimilarity', 'nested', 'fastasequence']

    # dictionary with 'number of CPUs':extension
    server_extensions = {2: 'c4.large', 8: 'c4.2xlarge'}

    html_code = ''

    def log(args):
        with open('log.txt', 'a') as f:
            if isinstance(args, list):
                for arg in args:
                    f.write(str(arg) + ' ')
            else:
                f.write(args)
            f.write('\n')

    def cgi_result(data, environ):
        """fakes a cgi result
        data: input data
        environ: environment variables
        """
        fake_stdin = StringIO.StringIO(data)
        fake_stdin.seek(0)
        fake_form = cgi.FieldStorage(fp=fake_stdin, environ=environ)
     return fake_form

    def html_output(new_line):
        """
        generates dynamic html output
        """
        global html_code
        html_code += new_line
        html_output = HEADER + html_code + END
        sys.__stdout__.write(new_line + '\n')
        sys.__stdout__.flush()

    # writes a sequence or sequence file to the data directory
    def write_sequence(sequence, index=None):
        if index is not None:
            fasta_filename = os.path.join(data_dir, '{}_{}_sequence.fasta'.format(run_name, index))
        else:
            fasta_filename = os.path.join(data_dir, '{}_sequence.fasta'.format(run_name))
        if sequence:
            sequence = clean_sequence(sequence)
            with open(fasta_filename, 'w') as fasta_file:
                fasta_file.write(sequence)
        else:
            return ''
        return fasta_filename

    html_output(HEADER)

    html_output('<div class="comment" id="submitted">Your job was submitted. Please be patient....<br><br></div>\n')

    # standard use via web
    if len(sys.argv) == 1:
        form = cgi.FieldStorage()
    # for debugging and unit testing
    elif len(sys.argv) > len(cgi_args):

        formdata = ''
        for i, _ in enumerate(cgi_args):
            formdata += '---123\nContent-Disposition: form-data; name="'
            formdata += cgi_args[i] + '"\n\n'
            formdata += sys.argv[1 + i] + '\n'
        formdata += '---123\nContent-Disposition: form-data; name="fastafile"; filename=""\nContent-Type: text/plain\n'
        formdata_environ = {
            'CONTENT_LENGTH': str(len(formdata)),
            'CONTENT_TYPE': 'multipart/form-data; boundary=-123',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'POST',
        }
        form = cgi_result(formdata, formdata_environ)

    # checks which algorithm/version is requested
    # imports the correct version of repeat_finder.py
    if form.getvalue('algorithm') == 'publication':
        from repeat_finder_publication import read_configfile
    elif form.getvalue('algorithm') == 'stable':
        from repeat_finder import read_configfile
    elif form.getvalue('algorithm') == 'beta':
        from repeat_finder_beta import read_configfile
    else:
        html_output('Algorithm version could not be determined. Exiting now.....')
        sys.exit(1)

    # read configuration file
    config_args = read_configfile(config_filename)
    data_dir = config_args['DATADIR']

    try:
        fasta_fileitem = form['fastafile']
        primer3_fileitem = form['primer3file']
    except KeyError:
        html_output('Error: Not started via a proper CGI form')
        sys.exit()

    nested = -1
    try:
        if form.getvalue('nested'):
            nested = form.getvalue('nested')
    except:
        html_output('Not started via a proper CGI form - Nested checkbox is missing')
    # checks if the sequence is OK

    # checks if the input file is OK

    # creates a random name for each run
    run_name = ''
    if form.getvalue('private'):
        # create a long runname which is not shown in results
        html_output(NOT_PUBLIC)
        while os.path.isfile(run_name) or run_name == '':
            run_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
    else:
        while os.path.isfile(run_name) or run_name == '':
            run_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))

    # Test if a sequence file was uploaded
    sequence = ''
    if fasta_fileitem.filename:
        for line in fasta_fileitem.file.readlines():
            sequence += line
    elif form.getvalue('fastasequence'):
        sequence = form.getvalue('fastasequence')
    else:
        html_output('Error: No valid FASTA sequence was provided<br>')

    # Test if a primer3 settings file was uploaded
    input_args.append('-PRIMER3_SETTINGS')
    if primer3_fileitem.filename:
        primer3_settings = primer3_fileitem.file.read()
        primer3_filename = data_dir + run_name + '_primer3.ini'
        with open(primer3_filename, 'w') as primer3_file:
            primer3_file.write(primer3_settings)
    else:
        primer3_filename = config_args['PRIMER3_SETTINGS']
    input_args.append(primer3_filename)

    if sequence.count('>') > 100:
        html_output(MAX_SEQUENCES)
    else:
        # finds the suitable AWS instance type depending on the number of jobs
        server_extension = ''
        for key in sorted(server_extensions.iterkeys()):
            if (sequence.count('>') / int(key)) > 5:
                server_extension = server_extensions[key]
                config_args['MAXTHREADS'] = key
        if server_extension == '':
            server_extension = server_extensions[2]

    sequence = sequence.strip()
    sequence_filename = write_sequence(sequence)
    input_args.append('-PRIMER3_DIRECTORY')
    input_args.append(config_args['PRIMER3_DIRECTORY'])
    input_args.append('-PRIMER3_EXE')
    input_args.append(config_args['PRIMER3_EXE'])
    input_args.append('-NESTED')
    input_args.append(nested)
    input_args.append('-MAXTHREADS')
    input_args.append(1)

    if int(form.getvalue('maxrepeats')) > 1 and int(form.getvalue('maxrepeats')) < 7:
        input_args.append('-MAXREPEATS')
        input_args.append(form.getvalue('maxrepeats'))
    else:
        html_output('Error: Please provide a value between 2 and 6 for the repeat length<br>')
    if int(form.getvalue('primerpairs')) > 0 and int(form.getvalue('primerpairs')) < 101:
        input_args.append('-PRIMERPAIRS')
        input_args.append(form.getvalue('primerpairs'))
    else:
        html_output('Error: Please provide a value between 1 and 100 for the number of primer pairs<br>')

    # write all input files
    # batchrun name
    if form.getvalue('batchname'):
        with open(data_dir + run_name + '_name.txt', 'w') as name_file:
            name_file.write(form.getvalue('batchname'))
    # primer3 settings
    if not primer3_fileitem.filename:
        copyfile(config_args['PRIMER3_SETTINGS'], data_dir + run_name + '_primer3.ini')
    # batchprimer settings
    with open(data_dir + run_name + '_batchprimer.ini', 'w') as batchprimer_file:
        for input_arg in input_args:
            batchprimer_file.write(str(input_arg) + '\n')

    if 'Error: ' not in html_code:
        if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
            html_output(
                '<div class="comment">Remote server will be started now. This might take a minute or two.<br></div>')

            new_servername = start_remote_server(config_args['GFSERVER'], config_args['SERVERNAME'],
                                                 config_args['SERVERPORT'], 120, server_extension)
            if not new_servername:
                html_output('Error: Compute server could not be started.<br><br>')
            else:
                config_args['SERVERNAME'] = new_servername
                html_output('<div class="comment"><br>Remote server is running now.<br><br></div>')

    remoteserver_url = None

    if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):

        # check for new DNS of AWS instance and replace old name
        aws = read_aws_conf()
        session = boto3.session.Session(aws_access_key_id=aws['aws_access_key_id'],
                                        aws_secret_access_key=aws['aws_secret_access_key'],
                                        region_name=aws['region_name'])
        ec2 = session.resource('ec2')
        instances = ec2.instances.all()
        compute_host = ''
        for instance in instances:
            instance_name = ''
            for tag in instance.tags:
                if 'Value' in tag:
                    if 'Key' in tag.keys() and 'Value' in tag.keys():
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
            if instance_name == config_args['SERVERNAME'] and compute_host == '':
                compute_host = instance.id
                # get the base hostname
                config_args['SERVERNAME'] = instance.private_dns_name.split('.')[0]
                remoteserver_url = 'http://' + instance.public_dns_name
                if not test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']):
                    html_output('<br>Server start was successful, but gfServer does not respond<br>')
    else:
        if config_args.get('SERVERURL') is not None:
            remoteserver_url = config_args['SERVERURL']
        else:
            remoteserver_url = 'http://localhost'
    if remoteserver_url is not None:
        baseurl = '{}:8003'.format(remoteserver_url)
        # checks if the REST server is responding
        url = '{}/myIP'.format(baseurl)
        try:
            req = urllib2.Request(url, )
            reply = ast.literal_eval(urllib2.urlopen(req).read())
        except:
            reply = {}
        if 'IP' not in reply.keys():
            html_output('<br>Rest server URL: {}'.format(remoteserver_url))
            html_output('<br>Error: Rest server is not responding')
        else:
            rest_url = reply['IP']
    else:
        html_output('<br>Error: Remote server has no URL<br>')

    if test_server(config_args['GFSERVER'], config_args['SERVERNAME'], config_args['SERVERPORT']) and \
            sequence_filename and 'Error: ' not in html_code:

        input_args.append('-SERVERNAME')
        input_args.append(config_args['SERVERNAME'])
        input_args.append('-SERVERPORT')
        input_args.append(config_args['SERVERPORT'])
        input_args.append('-GFSERVER')
        input_args.append(config_args['GFSERVER'])
        input_args.append('-GFPCR')
        input_args.append(config_args['GFPCR'])
        input_args.append('-DATADIR')
        input_args.append(config_args['DATADIR'])
        input_args.append('-RUNNAME')
        input_args.append(run_name)
        html_output(
            '<div class="comment" id="started">Hemi-NeSTR was just started. It will take about two minutes per sequence batch.<br></div>')

        with open(data_dir + run_name + '_results.txt', 'w') as result_file:
            result_file.write('Your job is still running. Just be patient and refresh the page in a couple of minutes.\n')

        sub_seqs = []
        offset = 0

        # needed to deal with different sequence formats (single or multiple)
        sequence = ' ' + sequence

        # splits multiple sequences into a list of sequences
        while offset != -1:
            offset = sequence.find('>', offset + 1)
            if offset != -1:
                sub_seqs.append(sequence[offset:sequence.find('>', offset + 1)].strip())

        base_args = input_args[:]

        seqs = []
        for i, _ in enumerate(sub_seqs):
            input_args = base_args[:]
            input_args.append('-RUNNAME')
            input_args.append('{}.{}'.format(run_name, i))
            seqs.append(input_args)
        log(input_args)

        html_output(STATUS.format(run_name))

        # read primer3 input paramters for all runs
        with open(primer3_filename, 'r') as f:
            primer3_params = str(f.read())

        for i, sub_seq in enumerate(sub_seqs):
            seq_name = sub_seq.splitlines()[0]
            seq_name = seq_name[0:seq_name.find(' ')][0:20]

            html_output(TABLE_ROW.format(i, seq_name))
            html_output(SCRIPT.format(i, run_name, rest_url))
            params = {'arguments': seqs[i],
                      'run_name': run_name + '.{}'.format(i),
                      'sequence': clean_sequence(sub_seqs[i] + '\n'),
                      'primer3_parameters': primer3_params}
            params_enc = urllib.urlencode(params)

            repeat_finder_request = urllib2.Request(baseurl + '/repeat_finder', params_enc)

            urllib2.urlopen(repeat_finder_request)

        html_output(RESULTS.format(run_name))

        results = {}
        while len(results) < len(sub_seqs):
            for i, _ in enumerate(sub_seqs):
                req = urllib2.Request('{}/job_result?run_name={}.{}'.format(baseurl, run_name, i), )
                reply = ast.literal_eval(urllib2.urlopen(req).read())
                if reply.get('status') == 'finished':
                    results[i] = reply.get('results')
                time.sleep(1)

        with open(os.path.join(data_dir, '{}_results.txt'.format(run_name)), 'w') as result_file:
            for i, _ in enumerate(sub_seqs):
                result_file.write(results[i] + '\n')
        html_output(SCRIPT_RESULTS)
    elif sequence_filename:
        html_output('Server is not ready, please try again later.<br>')

    html_output(end)
    sys.exit(0)


if __name__ == '__main__':
    main()
