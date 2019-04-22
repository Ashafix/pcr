#!/usr/bin/env python

# Tests if all the components of BatchPrimerDesign are working
import os
import subprocess
from repeat_finder import read_configfile, read_aws_conf
import boto3
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2


def test_server(gfserver, servername, serverport):

    command_line = '{} status {} {}'.format(gfserver, servername, serverport)
    try:
        gfserver_response = subprocess.check_output([command_line], shell=True, stderr=subprocess.STDOUT)
    except:
        return False

    if gfserver_response.startswith('Couldn'):
        return False
    return gfserver_response.find('version') >= 0 and gfserver_response.find('port') >= 0 and \
           gfserver_response.find('host') >= 0 and gfserver_response.find('type') >= 0


def main():
    config_filename = 'batchprimer.conf'
    conf_arguments = read_configfile(config_filename)

    remoteserver_url = ''

    message = ''
    message += 'Configuration file could '

    if conf_arguments == '':
        message += 'NOT be read<br>'
        message += 'NO further testing was possible to due a missing .conf file'
    else:
        message += 'be read<br><br>'
        message += str(conf_arguments) + '<br><br>'

    if conf_arguments != '':
        message += 'gfServer '
        if test_server(conf_arguments['GFSERVER'], conf_arguments['SERVERNAME'], conf_arguments['SERVERPORT']):
            message += 'is up and running<br>'
        else:
            # check if it is possible to find an AWS server with the same name
            aws = read_aws_conf()
            session = boto3.session.Session(aws_access_key_id=aws['aws_access_key_id'],
                                            aws_secret_access_key=aws['aws_secret_access_key'],
                                            region_name=aws['region_name'])
            ec2 = session.resource('ec2')
            instances = ec2.instances.all()
            instance_name = ''
            for instance in instances:
                for tag in instance.tags:
                    if 'Value' in tag and 'Key' in tag and instance_name == '':
                        if 'Key' in tag.keys() and 'Value' in tag.keys():
                            if tag['Key'] == 'Name':
                                if tag['Value'] == conf_arguments['SERVERNAME']:
                                    if test_server(conf_arguments['GFSERVER'], instance.private_dns_name.split('.')[0],
                                                   conf_arguments['SERVERPORT']):
                                        message += 'is up and running<br>'
                                        conf_arguments['SERVERNAME'] = instance.private_dns_name.split('.')[0]
                                        instance_name = tag['Value']
                                        remoteserver_url = 'http://' + instance.public_dns_name
            if instance_name == '':
                message += 'IS NOT running<br>'

        message += 'Primer3 executable'
        if os.path.isfile(conf_arguments['PRIMER3_EXE']):
            message += ' is found<br>'
        else:
            message += ' IS NOT found<br>'

        if remoteserver_url != '':
            message += '<br>REST server '
            # checks if the REST server is responding
            url = remoteserver_url + ':8003/cpuInfo'
            reply = ''
            try:
                req = urllib2.Request(url, )
                response = urllib2.urlopen(req)
                reply = str(response.read())
            except:
                pass
            if 'CPU' not in reply:
                message += ' URL: ' + remoteserver_url
                message += '<br>Error: Rest server is not responding'
            else:
                message += ' is responding correctly'
        else:
            message += '<br>Error: Remote server has no URL'

    message += '<form action="../primer.html"><input type="submit" value="Go back to start page"></form>'

    print("""\
    Content-Type: text/html\n
    <html><body>
    <p>{}</p>
    </body></html>
    """.format(message))


if __name__ == '__main__':
    main()

