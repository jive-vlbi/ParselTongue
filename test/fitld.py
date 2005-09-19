from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData

import os
import urllib

AIPS.userno = 1999

# Download a smallish FITS file from the EVN archive.
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
fitld.infile = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

try:
    print 'Antennas:', uvdata.antennas
    assert(len(uvdata.antennas) == 4)
    print 'Polarizations:', uvdata.polarizations
    assert(len(uvdata.polarizations) == 2)
    print 'Sources:', uvdata.sources
    assert(len(uvdata.sources) == 2)
    print 'Stokes:', uvdata.stokes
    assert(len(uvdata.stokes) == 4)

    sutable = uvdata.table('SU', 1)
    assert(sutable[0]['epoch'] == 2000.0)

    antable = uvdata.table('AN', 0)
    stabxyz = antable[3]['stabxyz']
    assert(3822846 < stabxyz[0] < 3822847)

finally:
    uvdata.zap()
