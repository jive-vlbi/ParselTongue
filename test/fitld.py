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
    pass

assert(not uvdata.exists())

fitld = AIPSTask('fitld')
fitld.datain = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

assert(uvdata.exists())

try:
    print 'Antennas:', uvdata.antennas
    assert(len(uvdata.antennas) == 4)
    print 'Polarizations:', uvdata.polarizations
    assert(len(uvdata.polarizations) == 2)
    print 'Sources:', uvdata.sources
    assert(len(uvdata.sources) == 2)
    print 'Stokes:', uvdata.stokes
    assert(len(uvdata.stokes) == 4)
    print 'Visibilities:', len(uvdata)
    assert(len(uvdata) == 36033)

    assert(uvdata.header.date_obs == '2003-02-25')

    sutable = uvdata.table('SU', 1)
    assert(sutable.version == 1)
    assert(sutable[0].epoch == 2000.0)

    antable = uvdata.table('AN', 0)
    assert(antable.version == 1)
    stabxyz = antable[3].stabxyz
    assert(3822846 < stabxyz[0] < 3822847)

    cltable = uvdata.table('CL', 0)
    start = cltable[0].time
    nxtable = uvdata.table('NX', 0)
    for row in nxtable:
        assert(row.time >= start)
    for row in nxtable:
        assert(sutable[row.source_id - 1].id__no == row.source_id)
    start2 = cltable[0]['time']
    assert(start2 == start)

    assert(uvdata.table_highver('NX') == 1)
    uvdata.table('NX', 0).zap()
    assert(uvdata.table_highver('NX') == 0)

    uvdata.clrstat()

finally:
    uvdata.zap()
