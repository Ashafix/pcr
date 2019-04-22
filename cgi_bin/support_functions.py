import sys
import os
import string
import time
import logging
import socket
import json
import urllib.urlencode
import urllib2
import nucleotide_tools as nt
from StreamToLogger import StreamToLogger
from testserver import test_server


def create_clean_filename(old_name):
    """
    cleans a filename
    """
    old_name = old_name.replace(' ', '_')
    # characters which are allowed in filename
    positive_list = string.ascii_letters + string.digits
    positive_list += '_#$%[]().'

    old_name = ''.join(i for i in old_name if i in positive_list)
    return old_name


def read_aws_conf(locations=('/var/www/data/', '/home/ubuntu/.aws/')):
    """
    reads the AWS credentials
    returns a dict with the values from the credentials file
    """

    aws = {}

    for location in locations:
        if os.path.isfile(location + 'credentials'):
            try:
                with open(location + 'credentials', 'r') as credentials:
                    aws['region_name'] = 'eu-central-1'
                    for line in credentials.readlines():
                        if '=' not in line:
                            continue
                        cells = line.split('=')
                        aws[cells[0].strip()] = cells[1].strip()

                return aws
            except:
                pass
    return aws

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
    output += ', '.join(nt.primer_stats(primer, primer3_output)) + ', {}\n'.format(amplicon_gc_content)

    return output


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


def start_remote_server(gfserver, servername, serverport, timeout, server_extension,
                        stdout=sys.stdout, waiting_period=0.25):
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

    stdout.write('Start remote server<br />{sep}Server name: {}{sep}<br />gfServer: {}{sep}'
                 '<br />Server port: {}{sep}<br />Time out: {}{sep}'.format(servername, gfserver, serverport, timeout,
                                                                            sep=os.linesep))

    aws = read_aws_conf()
    session = boto3.session.Session(aws_access_key_id=aws['aws_access_key_id'],
                                    aws_secret_access_key=aws['aws_secret_access_key'],
                                    region_name=aws['region_name'])
    ec2 = session.resource('ec2')

    instances = ec2.instances.all()
    if len(list(instances)) < 2:
        stdout.write('No second AWS instance was found!{sep}'.format(sep=os.linesep))
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
                stdout.write('<br /> Servername: {}<br />{sep}'.format(servername, sep=os.linesep))
                instance.start()
                # wait until the instance is up and running
                local_timeout = timeout
                while instance.state['Code'] != 16 and local_timeout > 0:
                    time.sleep(waiting_period)
                    local_timeout -= waiting_period
                if local_timeout < 0:
                    stdout.write('Server start was unsuccessful, the timeout period was exceeded{sep}'.format(sep=os.linesep))
                    return ''
                if not test_server(gfserver, servername, serverport):
                    stdout.write('Server start was successful, but gfServer does not respond{sep}'.format(sep=os.linesep))
                    return ''
                else:
                    return instance_name
    return ''


def execute_primer3(primer3_input, local_run_name, remote_server,
                    port=8003, waiting_period=2, max_time=1200):
    baseurl = '{}:{}'.format(remote_server, port)
    params = urllib.urlencode({'run_name': local_run_name, 'primer3_input': primer3_input})
    primer3_request = urllib2.Request(baseurl + '/primer3', params)
    urllib2.urlopen(primer3_request)
    primer3_status = ''

    while primer3_status != 'finished' and max_time > 0:
        time.sleep(waiting_period)
        max_time -= waiting_period
        params = urllib.urlencode({'run_name': local_run_name})
        primer3_url = urllib2.urlopen('{}/job_status?{}'.format(baseurl, params))
        primer3_response = primer3_url.read()
        if 'job_status' in primer3_response:
            try:
                primer3_status = json.loads(primer3_response)['job_status'][local_run_name]
            except (json.decoder.JSONDecodeError, KeyError):
                primer3_status = ''

    if max_time <= 0:
        return '', 'Primer3 failed to generate output in max time\n'

    primer3_url = urllib2.urlopen('{}/job_results?'.format(baseurl, params))
    primer3_output = primer3_url.read()
    while '\\n' in primer3_output:
        primer3_output = primer3_output.replace('\\n', '\n')
    primer3_output = primer3_output[1:-1] + '\n'
    return primer3_output, ''
