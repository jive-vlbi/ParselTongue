from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage

import os
import signal
import time
import urllib

AIPS.userno = 1999

# Download a smallish FITS file from the EVN archive.
url = 'http://archive.jive.nl/exp/N05L1_050301/pipe/n05l1_4C39.25_ICLN.FITS'
file = '/tmp/' + os.path.basename(url)
if not os.path.isfile(file):
    urllib.urlretrieve(url, file)
assert(os.path.isfile(file))

name = os.path.basename(url).split('_')[1].upper()
image = AIPSImage(name, 'ICLN', 1, 1)
if image.exists():
    image.zap()
    pass

assert(not image.exists())

fitld = AIPSTask('fitld')
fitld.datain = file
fitld.outdata = image
fitld.msgkill = 2
fitld()

assert(image.exists())

image.zap(force=True)

assert(not image.exists())
