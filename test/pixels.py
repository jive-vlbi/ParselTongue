from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage
from Wizardry.AIPSData import AIPSImage as WizAIPSImage

import os
from parseltest import urlretrieve

AIPS.userno = 1999

# Download a smallish FITS file from the EVN archive.
url = 'http://archive.jive.nl/exp/N05L1_050301/pipe/n05l1_4C39.25_ICLN.FITS'
file = '/tmp/' + os.path.basename(url)
if not os.path.isfile(file):
    urlretrieve(url, file)
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
fitld.go()

assert(image.exists())

try:
    image = WizAIPSImage(image)
    image.squeeze()
    image.pixels[0][0] = 0
    image.update()

    image = WizAIPSImage(image)
    image.squeeze()
    assert(image.pixels[0][0] == 0)

finally:
    image.zap()
