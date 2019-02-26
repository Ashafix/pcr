import ast


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


def count_amplicons(isPCRoutput, primerF, primerR):
    """
    Takes a list of isPCRoutputs and counts the numbers of amplicons for a primer pair
    """
    startpoint = isPCRoutput.find('{};{}\n'.format(primerF, primerR))
    if startpoint == -1:
        return -1
    if startpoint > 0 and isPCRoutput[startpoint - 1] != '\n':
        return -1

    isPCRfragment = isPCRoutput[startpoint:]
    if isPCRfragment.find(';', len(primerF) + len(primerR) + 2) > -1:
        isPCRfragment = isPCRfragment[0:isPCRfragment.find(';', len(primerF) + len(primerR) + 2)]

    return isPCRfragment.count('>')


def calculate_gc_content(sequence, precision=2):
    val = 100 * (float(sequence.count('G')) + float(sequence.count('C'))) / float(len(sequence))
    if precision is not None:
        return round(val, precision)
    return val
