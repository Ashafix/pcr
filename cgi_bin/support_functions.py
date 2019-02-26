import string


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
