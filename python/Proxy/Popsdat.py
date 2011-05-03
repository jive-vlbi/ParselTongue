# Copyright (C) 2005 Joint Institute for VLBI in Europe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

This module provides dictionaries of default values and string lengths
for AIPS adverbs generated from the POPSDAT.HLP help file.

"""

# Generic Python stuff.
import os

class Popsdat:
    def __parse(self):
        """Determine default values and string lengths for all AIPS
        tasks by parsing POPSDAT.HLP."""

        # POPSDAT.HLP contains some POPS statements that set default
        # values for arrays and strings.  Parse those statements first
        # such that we can use those default values below.
        self.__parse_statements()

        input = open(self.path)

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
                if name in self.default_dict:
                    value = [self.default_dict[name]]
                else:
                    value = [0.0]
                    pass

                dimensions = int(split_line[3])
                if dimensions == 1:     # Vector of floats.
                    length = int(float(split_line[4]))
                    self.default_dict[name] = [None] + length * value
                elif dimensions == 2:   # Matrix of floats.
                    dimy = int(float(split_line[4]))
                    dimx = int(float(split_line[5]))
                    self.default_dict[name] = [None] \
                                              + dimx * [[None] + dimy * value]
                else:
                    msg = "Cannot handle float arrays of dimension %d" \
                          % dimensions
                    raise AssertionError, msg
            elif type == 4:             # Verb
                self.verb_dict[name] = int(split_line[2])
            elif type == 6:             # End of adverbs.
                break
            elif type == 7:             # Array of characters.
                if name in self.default_dict:
                    value = self.default_dict[name]
                else:
                    value = ''
                    pass

                dimensions = int(split_line[3])
                self.strlen_dict[name] = int(float(split_line[4]))
                if dimensions == 1:     # String
                    self.default_dict[name] = value
                elif dimensions == 2:   # Vector of strings.
                    length = int(float(split_line[5]))
                    self.default_dict[name] = [None] + length * [value]
                else:
                    msg = "Cannot handle character arrays of dimension %d" \
                          % dimension
                    raise AssertionError, msg
            else:
                continue

        for line in input:
            # Older AIPS versions have some essential additional
            # adverbs that are defined in PROC DEFADV.
            if line.startswith('PROC DEFADV'):
                break
            continue

        for line in input:
            # The end of a PROC is marked by FINISH.
            if line.startswith('FINISH'):
                break

            split_line = line.split()
            type = split_line[0]

            if type == 'ARRAY':
                for array in split_line[1:]:
                    lparen = array.find('(')
                    rparen = array.find(')')
                    if lparen == -1 or rparen == -1:
                        continue
                    name = array[:lparen].lower()
                    dim = array[lparen+1:rparen]
                    dim = dim.split(',')
                    if len(dim) == 1:
                        length = int(dim[0])
                        self.default_dict[name] = [None] + length * [0.0]
                    elif len(dim) == 2:
                        dimx = int(dim[0])
                        dimy = int(dim[1])
                        self.default_dict[name] = [None] \
                                                  + dimx * [[None] \
                                                            + dimy *[0.0]]
                    else:
                        continue
                    continue
                pass
            elif type == 'SCALAR':
                for scalar in split_line[1:]:
                    name = scalar.rstrip(',').lower()
                    if name:
                        self.default_dict[name] = 0.0
                        pass
                    continue
                pass
            continue

    def __parse_statements(self):
        """Parse statements in POPSDAT.HLP."""

        input = open(self.path)

        for line in input:
            # Statements follow the adverbs.
            if line.startswith('QUITPOPS'):
                break;
            continue

        for line in input:
            if line.startswith('*'):
                break
            continue

        for line in input:
            if line.startswith('*'):
                break

            # If we have multiple statements on a line, split them.
            split_line = line.strip().split(';')
            for statement in split_line:
                if not statement:
                    continue

                # Parse statement.  This really only parses
                # assignments, but that's all we care about (for now).
                words = statement.strip().split('=')
                name = words[0].strip().lower()
                value = words[1].strip()
                if value.startswith("'"):
                    value = value.strip("'")
                else:
                    value = float(value)
                    pass

                # Set temporary default value.  The permanent default
                # value will be set later.
                self.default_dict[name] = value
            continue

    def __init__(self, version):
        self.default_dict = {}
        self.strlen_dict = {}
        self.verb_dict = {}

        self.version = version
        self.path = self.version + '/HELP/POPSDAT.HLP'
        if not os.path.exists(self.path):
            self.version = os.environ['AIPS_VERSION']
            self.path = self.version + '/HELP/POPSDAT.HLP'

        self.__parse()
