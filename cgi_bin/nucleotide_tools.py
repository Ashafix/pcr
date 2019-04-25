import ast
import string


with open('ssr_list.txt', 'r') as f:
    ssr_list = ast.literal_eval(f.read())


def similarity(oligo1, oligo2):
    """
    determines the similarity between two oligos
    searches for the longest overlap
    X is used a placeholder, so it will match any character
    """
    if len(oligo2) > len(oligo1):
        oligo1, oligo2 = oligo2, oligo1
    if len(oligo1) == 0 or len(oligo2) == 0:
        return float(0)
    oligo1 = 'X' * len(oligo1) + oligo1 + 'X' * len(oligo1)
    best_score = 0

    for i in range(len(oligo1) - len(oligo2)):
        score = 0
        for j in range(len(oligo2)):
            if oligo1[i + j] == oligo2[j]:
                score += 1
        best_score = max(score, best_score)
    return float(best_score) / float(len(oligo2))


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


def reverse_complement(seq):
    seq = seq.upper()
    return seq.replace('G', 'c').replace('C', 'g').replace('A', 't').replace('T', 'a').upper()[::-1]


def dinucleotide_repeat(sequence):
    """
    finds the length of dinucleotide repeats in a sequence, i.e. ACTAGAGAGTCA would return 6
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


def find_repeats(sequence, max_length):
    """
    finds the longest repeat in a given sequence
    max_length of repeat unit
    """
    longest_repeat = ''

    for ssr in ssr_list:
        if len(ssr) <= int(max_length):
            i = 0
            while ssr * i in sequence:
                i += 1

            if len(ssr * i) > len(longest_repeat) and i > 1:
                longest_repeat = ssr * i

    return longest_repeat


def exclude_list(sequence):
    """
    Creates a list of sequences which should be excluded from primer binding sites
    """
    to_exclude = []
    sequence = sequence.upper()
    for ssr in ssr_list:
        if len(ssr) > 3:
            continue
        max_length = 0
        for i in range(1, int(round(len(sequence) / 2, 0))):
            if ssr * i in sequence and i * len(ssr) >= 9:
                max_length = i
        if max_length > 0:
            to_exclude.append(ssr * max_length)
    return to_exclude


def count_amplicons(isPCRoutput, primer):
    """
    Takes a list of isPCRoutputs and counts the numbers of amplicons for a primer pair
    """
    startpoint = isPCRoutput.find('{};{}\n'.format(primer.forward, primer.reverse))
    if startpoint == -1:
        return -1
    if startpoint > 0 and isPCRoutput[startpoint - 1] != '\n':
        return -1

    isPCRfragment = isPCRoutput[startpoint:]
    if isPCRfragment.find(';', len(primer.forward) + len(primer.reverse) + 2) > -1:
        isPCRfragment = isPCRfragment[0:isPCRfragment.find(';', len(primer.forward) + len(primer.reverse) + 2)]

    return isPCRfragment.count('>')


def calculate_gc_content(sequence, precision=2):
    val = 100 * (float(sequence.count('G')) + float(sequence.count('C'))) / float(len(sequence))
    if precision is not None:
        return round(val, precision)
    return val


def check_specificity(primer, targetSequence, isPCRoutput):
    """
    takes a primer pair, a input sequence for which the primers were designed and checks in the isPCRoutput if the target sequence is amplified or something else
    also checks if the number of amplicons is exactly one
    return:
        True: if primerF and primerR are in targetSequence and only amplicon is amplified
        False: if any of the above criteria are not met
    """

    # checks if only one is amplicon created, if yes, continue, otherwise break the function
    if count_amplicons(isPCRoutput, primer) != 1:
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
            # TODO impossible to reach that piece of code!!!
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


def is_valid_fasta(sequence):
    """
    checks if a FASTA file is correct
    """
    header = False  # indicates whether a header was found
    sequence = sequence.strip()
    if not sequence.startswith('>'):
        return False
    fasta_lines = sequence.split('\n')
    if len(fasta_lines) < 2:
        return False
    for fasta_line in fasta_lines:
        if fasta_line.startswith('>'):
            if header:
                return False
            header = True
        else:
            if not header:
                return False
            header = False
            fasta_line = fasta_line.upper()
            if not all(nuc in 'ATGC\n\r' for nuc in fasta_line):
                return False
    return True


def clean_sequence(sequence):
    """
    cleans a FASTA nucleotide sequence
    """
    new_sequence = ''
    nucleotides = 'ATGC'
    legal_header = string.ascii_lowercase + string.ascii_uppercase + string.digits + "_=:'+- "
    for line in sequence.splitlines():
        if line.startswith('>'):
            new_sequence += '>'
            new_sequence += ''.join(header for header in line if header in legal_header)
            new_sequence += '\n'
        else:
            line = line.upper()
            new_sequence += ''.join(nuc for nuc in line if nuc in nucleotides)
            new_sequence += '\n'
    return new_sequence
