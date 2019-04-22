class RepeatFinder:
    def __init__(self, args=None, max_threads=1, max_similarity=1, nested=0):
        self.fasta = None
        self.gfpcr = None
        self.gfserver = None
        self.maxrepeats = None
        self.maxthreads = max_threads
        self.max_similarity = max_similarity
        self.nested = nested
        self.output = None
        self.primer3_directory = None
        self.primer3_exe = None
        self.primer3_settings = None
        self.primerpairs = None
        self.remoteserver = None
        self.removetempfiles = None
        self.runname = None
        self.servername = None
        self.serverport = None
        self.shutdown = None
        self.timeout = None
        self.waitingperiod = None

        # if args is coming from an ArgParse object
        if args is not None:
            for att, value in args.__dict__.items():
                if att.startswith('_'):
                    continue
                if value is None:
                    continue
                setattr(self, att.lower(), value)

        self._gfserver()
        self._validate()

    def _validate(self):
        if self.nested not in (-1, 0, 1):
            raise ValueError('nested must be either -1, 0 or 1')
        if self.maxthreads < 1:
            raise ValueError('max_threads needs to be 1 or higher')
        if not os.path.isfile(self.fasta_filename):
            raise ValueError('Fasta file {} could not be found'.format(self.fasta_filename))
        if not os.path.isfile(self.standard_primer_settings_filename):
            raise ValueError('Primer3 settings file {} could not be found'.format(self.standard_primer_settings_filename))
        if not os.path.isfile(self.primer3_exe):
            raise ValueError('Primer3 executable {} could not be found'.format(self.primer3_exe))
        if not os.path.isfile(self.gfpcr):
            raise ValueError('gfPCR executable {} could not be found'.format(self.gfpcr))
        if not os.path.isdir(self.primer3_directory):
            raise ValueError('Primer3 directory {} does not exist'.format(self.primer3_directory))
        if self.serverport <= 0:
            raise ValueError('Please specificy a legal numerical value for the server port, got {}'.format(self.serverport))
        if int(self.maxrepeats) < 0:
            print('Please specificy a legal numerical value for the max repeats, got {}'.format(self.maxrepeats))
        if self.max_primerpairs < 0:
            print('Please specificy a legal numerical value for the max primer pairs, got {}'.format(self.max_primerpairs))
        # test if the in-silico PCR server is ready
        if not self.gfserver.test_server():
            if remote_server == '':
                raise RuntimeError('gfServer not ready, please start it')
            else:
                print(self.run_name + ' gfServer not ready, it is started now')
                if start_remote_server(self.servername) != '':
                    print(self.run_name + ' Remote server was successfully started')
                else:
                    print(self.run_name + ' Remote server could not be started')

    # location of hg18.2bit
    pcr_location = gfPCR[0:len(gfPCR) - len('gfPCR')]

    def _gfserver(self):
        self.gfserver = GfServer(self.gfserver, self.servername, self.serverport)

    def run_gfpcr(self, primer):
        """

        :param primer:
        :return:
        """
        cmd = [self.gfpcr, self.servername, str(self.serverport),
               self.pcr_location, primer.forward, primer.reverse, 'stdout']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        return process.communicate()[0]

    def run_primer3(self, primer3_input):
        process = subprocess.Popen(self.primer3_exe,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        process.stdin.write(primer3_input)
        return process.communicate()[0]

    def get_primers(self, sequence):
        """
        main function
        finds primers for a given sequence
        """
        # creates primer3 input file for each sequence
        output = ''
        stdoutput = ''
        header, sequence = sequence.split('\n', 1)
        header = header[1:]
        sequence = sequence.replace('\n', '').strip()

        if not nt.check_fasta('>{}\n{}'.format(header, sequence), 'NUCLEOTIDE', False):
            stdoutput += 'Sequence did not match FASTA format, no primers were designed\n'
            output = stdoutput
            return output, stdoutput

        create_primer3_file(header, sequence, nt.find_repeats(sequence, self.maxrepeats), nt.exclude_list(sequence),
                            Primer('', '', validate=False), self.primer3_directory, standard_primer_settings_filename)

        stdoutput += 'Primer3 will be started now, please be patient\n'

        filename = 'primer3_{}.txt'.format(create_clean_filename(header))

        with open(os.path.join(self.primer3_directory, filename), 'ru') as temp_file:
            primer3_input = ''.join(temp_file.readlines())
        temp_file.close()

        stdoutput += 'Primer3 subprocess started\n'
        if remote_server != '':
            local_run_name = '{}_{}'.format(self.run_name, os.getpid())
            primer3_output, comment = execute_primer3(primer3_input, local_run_name)
            stdoutput += comment
        else:
            orig_stdout = sys.stdout
            with open(str(os.getpid()) + ".out", "w") as f:
                sys.stdout = f
                primer3_output = self.run_primer3(primer3_input) + '\n'
            sys.stdout = orig_stdout
        stdoutput += 'Primer3 finished\n'
        primer3_list = []

        for lines in primer3_output.split('\n'):
            if lines.startswith('SEQUENCE_ID'):
                primer3_list.append(lines)
            elif lines.find('SEQUENCE=') > 0:
                if lines.startswith('PRIMER_LEFT') or lines.startswith('PRIMER_RIGHT'):
                    primer3_list.append(lines[lines.find('=') + 1:])
        print(self.run_name + " ##################")

        isPCRoutput = ''

        # list of primers which only amplify one amplicon
        accepted_primers = []

        # list of primers which can be used to search for nested primers
        accepted_nested_templates = []

        # Step 4: checks all created primers
        output += '==========\nTarget:, {}\n\n'.format(primer3_list[0][primer3_list[0].find('=') + 1:])

        for i in range(1, len(primer3_list), 2):
            if len(accepted_primers) >= self.max_primerpairs:
                break
            primer = Primer(primer3_list[i], primer3_list[i + 1])
            # checks if the primers do not contain repeats, e.g. GAGAGA, not longer than 2x2 repeat
            # if not, runs isPCR to see if they are specific
            if nt.dinucleotide_repeat(primer.forward) >= 6 or nt.dinucleotide_repeat(primer.reverse) >= 6:
                no_amplicons = 0
                stdoutput += '{} rejected, repeats\n'.format(primer.format())
            else:
                isPCRoutput = '{}\n{}'.format(primer.format(';'), self.run_gfpcr(primer))
                no_amplicons = nt.count_amplicons(isPCRoutput, primer)

            i += 1  # TODO check if that's correct, i += 2 ?!

            # checks if the primer pair amplifies only one amplicon
            if no_amplicons == 1:
                amplicon = get_amplicon_from_primer3output(primer, primer3_output)

                # checks if the primer pair amplifies the original target sequence
                # should be checked against all primers, not only the first pair
                if check_specificity(primer, amplicon, isPCRoutput):

                    if len(accepted_primers) == 0:
                        primer_1st = Primer(primer.forward, primer.reverse)
                        accept_primerpair = True
                    else:
                        accept_primerpair = nt.similarity(primer.forward, primer_1st.forward) < self.max_similarity and nt.similarity(primer.reverse, primer_1st.reverse) < self.max_similarity

                    # if the pair is accepted it will be written to the output file
                    if accept_primerpair and self.nested != 1:
                        accepted_primers.append(primer.format(','))
                        output += make_output(primer.forward, primer.reverse, amplicon, isPCRoutput, primer3_output)
                        stdoutput += output + '\n'
                    # v1.03
                    elif accept_primerpair and self.nested == 1:
                        accepted_nested_templates.append(primer.format())
            else:
                stdoutput += '{} rejected, not exactly one amplicon\n'.format(primer.format())
            # checks if not enough suitable primer pairs have been found
            # then tries to design primers for nested PCR
            # if yes, tries to redesign primers with identical reverse primer but different forward primer

            make_nested_primers = False
            if len(accepted_primers) == 0 and self.nested != 1:
                if i + 1 >= len(primer3_list):
                    stdoutput += 'no suitable primer pairs could be found, consider relaxing the primer3 parameters\n'
                elif i != 0 and i + 1 < len(primer3_list) and primer3_list[i + 1].startswith('SEQUENCE_ID'):
                    stdoutput += 'no suitable primer pairs could be found, consider relaxing the primer3 parameters\n'

            elif len(accepted_primers) != 0 and len(accepted_primers) < max_primerpairs and self.nested != -1:
                if i + 1 >= len(primer3_list):
                    make_nested_primers = True
                elif i != 0 and i + 1 < len(primer3_list) and primer3_list[i + 1].startswith('SEQUENCE_ID'):
                    make_nested_primers = True

            if make_nested_primers and self.nested == 0:
                stdoutput += 'trying to find nested primers\n'

                primer3_nested_output = ''
                primerF_nested = ''
                # creates new primer3 file with fixed reverse primer
                create_primer3_file(header, sequence, nt.find_repeats(sequence, self.max_repeats),
                                    nt.exclude_list(sequence), primer_1st, self.primer3_directory,
                                    standard_primer_settings_filename)
                filename = 'primer3_{}.txt'.format(create_clean_filename(header))
                with open(os.path.join(self.primer3_directory, filename), 'ru') as temp_file:
                    primer3_input = ''.join(temp_file.readlines())
                if self.remote_server != '':
                    execute_primer3(primer3_input, local_run_name)
                else:
                    primer3_nested_output += self.run_primer3(primer3_input) + '\n'
                stdoutput += 'Primer3 for nested primers finished\n'
                for lines in primer3_nested_output.split('\n'):
                    if lines.find('SEQUENCE') <= 0:
                        continue
                    if lines.startswith('PRIMER_LEFT'):
                        primer_nested_forward = lines[lines.find('=') + 1:]
                    elif lines.startswith('PRIMER_RIGHT'):
                        primer_nested = Primer(primer_nested_forward, lines[lines.find('=') + 1:])
                        # checks if the new, nested primer pair is specific
                        amplicon = get_amplicon_from_primer3output(primerF_nested, primer_nested)

                        if nt.dinucleotide_repeat(primer_nested.forward) >= 6 or nt.dinucleotide_repeat(
                                primer_nested.reverse) >= 6:
                            stdoutput += '{} rejected, repeats\n'.format(primer_nested.format())
                        else:
                            isPCRoutput_nested = '{}\n{}'.format(primer_nested.format(';'),
                                                                 self.run_gfpcr(primer_nested))

                            if check_specificity(primer_nested, amplicon, isPCRoutput_nested):
                                if nt.similarity(primer_nested.forward, primer_1st.forward) < self.max_similarity:
                                    stdoutput += '{} found nested primer\n'.format(primer_nested.format())
                                    accepted_primers.append(primer_nested.format(','))
                                    output += make_output(primer_nested, amplicon,
                                                          isPCRoutput_nested, primer3_nested_output)
                                    stdoutput += output + '\n'
                                    break
                                else:
                                    stdoutput += '{} too similar\n'.format(primer_nested.format())
                            else:
                                stdoutput += '{} not specific\n'.format(primer_nested.format())

                if len(accepted_primers) < max_primerpairs:
                    stdoutput += 'Not enough primer pairs could be found\n'
                    max_primerpairs = 0
            ####
            # added in v1.03 for forced nested primers
            elif self.nested == 1 and (i + 1 >= len(primer3_list) or (
                    i != 0 and primer3_list[i + 1].startswith('SEQUENCE_ID'))) and len(
                    accepted_nested_templates) > 0:
                stdoutput += 'forced to trying to find nested primers\n'
                # creates new primer3 file with fixed reverse primer
                for accepted_nested_template in accepted_nested_templates:
                    if len(accepted_primers) < max_primerpairs:
                        primer_1st = Primer(accepted_nested_template[0:accepted_nested_template.find(',')],
                                            accepted_nested_template[accepted_nested_template.find(',') + 1:])
                        create_primer3_file(header, sequence, nt.find_repeats(sequence, self.max_repeats),
                                            nt.exclude_list(sequence), primer_1st, self.primer3_directory,
                                            self.standard_primer_settings_filename)
                        filename = 'primer3_{}.txt'.format(create_clean_filename(header))
                        primer3_input = ''
                        with open(os.path.join(self.primer3_directory, filename), 'ru') as temp_file:
                            primer3_input += ''.join(temp_file.readlines())

                        primer3_nested_output, comment = execute_primer3(primer3_input,
                                                                         '{}nested{}'.format(filename,
                                                                                             random.random()))
                        stdoutput += comment
                        primer3_nested_output += primer3_nested_output + '\n'

                        for lines in primer3_nested_output.split('\n'):
                            if lines.find('SEQUENCE') <= 0:
                                continue
                            if lines.startswith('PRIMER_LEFT'):
                                primer_nested_forward = lines[lines.find('=') + 1:]

                            elif lines.startswith('PRIMER_RIGHT'):

                                primer_nested = Primer(primer_nested_forward, lines[lines.find('=') + 1:])
                                # checks if the new, nested primer pair is specific
                                amplicon = get_amplicon_from_primer3output(primer_nested, primer3_nested_output)

                                if nt.dinucleotide_repeat(primer_nested.forward) >= 6 or nt.dinucleotide_repeat(
                                        primer_nested.reverse) >= 6:
                                    stdoutput += '{} rejected, repeats\n'.format(primer_nested.format())
                                else:
                                    isPCRoutput_nested = '{}\n{}'.format(primer_nested.format(';'),
                                                                         self.run_gfpcr(primer_nested))

                                    if check_specificity(primer_nested, amplicon, isPCRoutput_nested):
                                        if nt.similarity(primer_nested.forward, primer_1st.forward) < self.max_similarity:
                                            stdoutput += '{} {} found forced nested primer\n'.format(
                                                primer_1st.forward,
                                                primer_nested.reverse)
                                            accepted_primers.append(primer_1st.format(','))
                                            accepted_primers.append(primer_nested.format(','))

                                            isPCRoutput = '{}\n{}'.format(primer_1st.format(';'),
                                                                          self.run_gfpcr(primer_1st))
                                            amplicon = get_amplicon_from_primer3output(primer_1st, primer3_output)
                                            output += make_output(primer_1st, amplicon, isPCRoutput, primer3_output)
                                            # should fix the problem with the doubled amplicon
                                            amplicon = get_amplicon_from_primer3output(primer_nested,
                                                                                       primer3_nested_output)
                                            output += make_output(primer_nested, amplicon,
                                                                  isPCRoutput_nested, primer3_nested_output)
                                            stdoutput += output + '\n'
                                            break
                                        else:
                                            stdoutput += '{} {} too similar\n'.format(primer_1st.forward,
                                                                                      primer_nested.reverse)
                                    else:
                                        stdoutput += '{} not specific\n'.format(primer_nested.format())

                stdoutput += 'Primer3 for forced nested primers finished\n'

        if (len(accepted_primers) < max_primerpairs and self.nested == -1) or (len(accepted_primers) < 2 and self.nested != -1):
            stdoutput += 'not enough primer pairs found\n'

        with open(str(os.getpid()) + ".tmp", "w") as temp:
            temp.write(output)
            temp.write(stdoutput)

        return output, stdoutput


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
