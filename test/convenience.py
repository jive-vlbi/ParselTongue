from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage, AIPSUVData

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

fitld = AIPSTask('fitld')
fitld.datain = file
fitld.outdata = image
fitld.go()

try:
    print 'Stokes:', image.stokes
    assert(len(image.stokes) == 1)

    # Download a second smallish FITS file from the EVN archive.
    url = 'http://archive.jive.nl/exp/N03L1_030225/fits/n03l1_1_1.IDI1'
    file = '/tmp/' + os.path.basename(url)
    if not os.path.isfile(file):
        urllib.urlretrieve(url, file)
    assert(os.path.isfile(file))

    name = os.path.basename(url).split('_')[0].upper()
    uvdata = AIPSUVData(name, 'UVDATA', 1, 1)
    if uvdata.exists():
        uvdata.zap()

    fitld = AIPSTask('fitld')
    fitld.datain = file
    fitld.outdata = uvdata
    fitld.go()

    try:
        print 'Stokes:', uvdata.stokes
        assert(len(uvdata.stokes) == 4)
    finally:
        uvdata.zap()
    
finally:
    image.zap()
