# Start an interactive ParselTongue session.

# Global AIPS defaults
from AIPS import AIPS

# The main classes ParselTongue provides.
from AIPSTask import *
from AIPSData import *

# Use our own, somewhat restricted rlcompleter.
import readline, ptcompleter
readline.parse_and_bind("tab: complete")

# This is not a batch job.
AIPSTask.isbatch = 0

# Seperate the blurb below from what the Python interpreter spits out.
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
