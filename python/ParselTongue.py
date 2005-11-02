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
This module provides support for starting an interactive ParselTongue
session.

"""

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
 
# Use our own, somewhat restricted, rlcompleter.
import readline, ptcompleter
readline.parse_and_bind("tab: complete")

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

# This is not a batch job.
AIPSTask.isbatch = 0

# Separate the blurb below from what the Python interpreter spits out.
print ""

print "Welcome to ParselTongue"
while True:
    try:
        input = raw_input("Please enter your AIPS user ID number: ")
        AIPS.userno = int(input)
    except KeyboardInterrupt:
        print ""
        print "AIPS user ID number is not set"
        break
    except:
        print "That is not a valid AIPS user ID number"
        continue
    else:
        break
