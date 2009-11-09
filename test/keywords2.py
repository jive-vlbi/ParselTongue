import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage
from Wizardry.AIPSData import AIPSImage as WizAIPSImage

import math
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
fitld.go()

assert(image.exists())

try:
    image = WizAIPSImage(image)

    parangle = image.keywords['PARANGLE']
    image.keywords['PARANGLE'] *= 2
    image.keywords['PI'] = math.pi
    image.keywords['ARRNAM'] = 'EVN'
    image.keywords.update()

    image = AIPSImage(image)
    assert(image.keywords['PARANGLE'] == 2 * parangle)
    assert(abs(image.keywords['PI'] - math.pi) < 1e-7)
    arrnam = image.keywords['ARRNAM']
    assert(arrnam.strip() == 'EVN')

finally:
    image.zap()
