"""

This module provides dictionaries of default values and string lengths
for AIPS adverbs generated from the POPSDAT.HLP help file.  These
dictionaries are pickled to avoid parsing POPSDAT.HLP again and again.

"""

# Generic Python stuff.
import os, pickle

class Popsdat:
    def __parse(self):
        """Determine default values and string lengths for all AIPS
        tasks by parsing POPSDAT.HLP."""

        path = os.environ['AIPS_ROOT'] + '/' + self.version \
               + '/HELP/POPSDAT.HLP'
        input = open(path)

        for line in input:
            # A line of dashes starts the parameter definitions.
            if line.startswith('--------'):
                break
            continue

        for line in input:
            # Comment lines start with ';' or 'C-'.
            if line.startswith(';') or line.startswith('C-'):
                continue

            split_line = line.split()
            name = split_line[0].lower()
            type = int(split_line[2])

            if type == 1:               # Float
                self.default_dict[name] = float(split_line[3])
            elif type == 2:             # Array of floats.
                dimensions = int(split_line[3])
                if dimensions == 1:     # Vector of floats.
                    length = int(float(split_line[4]))
                    self.default_dict[name] = length * [0.0]
                elif dimensions == 2:   # Matrix of floats.
                    dimy = int(float(split_line[4]))
                    dimx = int(float(split_line[5]))
                    self.default_dict[name] = dimx * [ dimy * [0.0]]
                else:
                    raise AssertionError
            elif type == 4:             # Verb
                self.verb_dict[name] = int(split_line[2])
            elif type == 6:             # End of adverbs.
                break
            elif type == 7:             # Array of characters.
                dimensions = int(split_line[3])
                self.strlen_dict[name] = int(float(split_line[4]))
                if dimensions == 1:     # String
                    self.default_dict[name] = ''
                elif dimensions == 2:   # Vector of strings.
                    length = int(float(split_line[5]))
                    self.default_dict[name] = length * ['']
                else:
                    raise AssertionError
            else:
                continue

    def __init__(self, version):
        self.default_dict = {}
        self.strlen_dict = {}
        self.verb_dict = {}

        assert(not version in ['OLD', 'NEW', 'TST'])
        self.version = version

        path = os.environ['HOME'] + '/.ParselTongue/' \
               + self.version + '/' + 'popsdat.pickle'

        try:
            unpickler = pickle.Unpickler(open(path))
            self.default_dict = unpickler.load()
            self.strlen_dict = unpickler.load()
            self.verb_dict = unpickler.load()
        except IOError, EOFError:
            self.__parse()

            # Make sure the directory exists.
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            pickler = pickle.Pickler(open(path, mode='w'))
            pickler.dump(self.default_dict)
            pickler.dump(self.strlen_dict)
            pickler.dump(self.verb_dict)
