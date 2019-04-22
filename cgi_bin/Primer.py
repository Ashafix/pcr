class Primer:
    def __init__(self, forward, reverse, validate=True):
        self.forward = forward.strip().upper()
        self.reverse = reverse.strip().upper()
        self.validate = validate
        if validate:
            self._validate()

    def __str__(self):
        return 'Primer: forward: {}; reverse: {}'.format(self.forward, self.reverse)

    def __repr__(self):
        return "Primer('{}', '{}', validate={})".format(self.forward, self.reverse, self.validate)

    def __eq__(self, other):
        return (self.forward == other.forward and self.reverse == other.reverse) or (self.forward == other.reverse and self.reverse == other.forward)

    def _validate(self):
        nucleotides = set('ATGC')
        if not set(self.forward).issubset(nucleotides) or not set(self.reverse).issubset(nucleotides):
            raise ValueError('got invalid sequence, only ATGC is allowed, got {} and {}'.format(self.forward,
                                                                                                self.reverse))
        if len(self.forward) == 0 or len(self.reverse) == 0:
            raise ValueError('both forward and reverse primer must have at least 1 nucleotide')

    def format(self, sep=' '):
        return '{}{sep}{}'.format(self.forward, self.reverse, sep=sep)
