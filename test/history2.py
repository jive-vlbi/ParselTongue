from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage
from Wizardry.AIPSData import AIPSImage as WizAIPSImage

import os
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
#fitld.msgkill = 2
fitld.go()

assert(image.exists())

try:
    count = 0
    for record in image.history:
        #print record
        if record[0:5] == 'FRING':
            count += 1
            pass
        continue
    assert(count > 5)

    image = WizAIPSImage(image)
    history = image.history
    history.append('Something new!')
    history.close()

    image = AIPSImage(image)
    seen = 0
    for record in image.history:
        #print record
        if record[0:5] == 'Somet':
            seen = 1
            pass
        continue
    assert(seen)

finally:
    image.zap()
