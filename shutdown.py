#!/usr/bin/env python

import os
import boto3
import sys
from time import sleep, time
from repeat_finder import read_aws_conf
import socket
import psutil

if len(sys.argv) < 2:
	print ('No data directory specified')
	sys.exit(0)
else:
	data_dir = sys.argv[1]

#reads the AWS conf file to get the keys
aws = read_aws_conf()

#establishes a session and gets the host name
session = boto3.session.Session(aws_access_key_id = aws['aws_access_key_id'], 
	aws_secret_access_key = aws['aws_secret_access_key'], 
	region_name = aws['region_name'])
ec2 = session.resource('ec2')
instances = ec2.instances.all()
hostname = socket.gethostbyaddr(socket.gethostname())[0]
compute_host = ''
for instance in instances:
	if instance.private_dns_name == hostname:
		compute_host = instance
if compute_host == '':
	print ('Could not resolve own instance ID')
	sys.exit()

#sleeps for 30 min to prevent immediate shutdown
sleep(1800)
while True:
	file_list = []
	file_list = [(os.path.getmtime(data_dir + fn), os.path.basename(data_dir + fn))
		for fn in os.listdir(data_dir)]
	file_list.sort()
	newest = file_list[len(file_list) - 1][0]

	#shuts the compute host down 50 min after the last job
	if ((time() - newest) / 60) > 50:
		#checks if the instance is idle
		if int(psutil.cpu_percent()) < 10:
			print ('Compute server will be shutdown now')
			response = compute_host.stop(DryRun = False, Force = False)
	#otherwise cleans up the file system, marks every file which is older than 60 days
	else:
		i = 0
		while i < len(file_list):
			if ((time() - file_list[i][0]) / 60 / 60 / 24) > 30:
				print ('old file' + file_list[i][1])
				i += 1
			else:
				i = len(file_list)
	sleep(60)
