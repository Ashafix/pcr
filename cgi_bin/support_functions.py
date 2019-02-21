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


def reverse_complement(seq):
    seq = seq.upper()
    return seq.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]
