# Copyright (C) 2005, 2006 Joint Institute for VLBI in Europe
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
This module provides support for starting an interactive ParselTongue
session.

"""

# ParselTongue version
import ptversion

# Global AIPS defaults
import AIPS

# Global FITS defaults
from FITS import FITS

# The main classes ParselTongue provides.
from AIPSTask import *
from AIPSData import *
from AIPSTV import *
from ObitTask import *
from FITSData import *
 
# Use our own, somewhat restricted, rlcompleter.  Don't fall over if
# readline isn't available though.
try:
    import atexit, readline, ptcompleter
    if __name__ == "__main__" :
        try:
            if 'PT_HISTORY' in os.environ:
                path = os.environ['PT_HISTORY']
            else:
                path = os.environ['HOME'] + '/.ParselTongue/history'
                pass
            readline.read_history_file(path)
        except IOError:
            pass
        readline.parse_and_bind("tab: complete")
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            pass
        atexit.register(readline.write_history_file, path)
except:
    pass

# Override help() such that it prints something useful for instances
# of AIPSTask.
_help = help
def help(obj):
    if isinstance(obj, AIPSTask):
        obj.help()
    else:
        _help(obj)
        pass
    return

def explain(obj):
    obj.explain()
    return

if __name__ == "__main__" :
        # This is not a batch job.
        AIPSTask.isbatch = 0

        # Separate the blurb below from what the Python interpreter spits out.
        print("")

        print("Welcome to ParselTongue", ptversion.version)
        while True:
                try:
                        input = input("Please enter your AIPS user ID number: ")
                        AIPS.userno = int(input)
                except KeyboardInterrupt:
                        print("")
                        print("AIPS user ID number is not set")
                        break
                except:
                        print("That is not a valid AIPS user ID number")
                        continue
                else:
                        break
