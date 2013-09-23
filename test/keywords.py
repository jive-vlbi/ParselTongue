import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData
from Wizardry.AIPSData import AIPSUVData as WizAIPSUVData

import math
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
fitld.datain = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

try:
    uvdata = WizAIPSUVData(name, 'UVDATA', 1, 1)

    antable = uvdata.table('AN', 0)
    arrnam = antable.keywords['ARRNAM']
    assert (arrnam.strip() == 'EVN')
    assert (antable.keywords['FREQID'] == -1)
    assert (antable.keywords['FREQ'] == 1642490000.0)
    assert (antable.keywords['IATUTC'] != 33.0)
    antable.keywords['ARRNAM'] = 'VLBA'
    antable.keywords['FREQID'] = 1
    antable.keywords['FREQ'] = 4974990000.0
    antable.keywords['IATUTC'] = 33.0
    antable.keywords['E'] = math.e
    antable.keywords['OPERATOR'] = 'NRAO'
    antable.close()

    antable = uvdata.table('AN', 0)
    arrnam = antable.keywords['ARRNAM']
    assert (arrnam.strip() == 'VLBA')
    assert (antable.keywords['FREQID'] == 1)
    assert (antable.keywords['FREQ'] == 4974990000.0)
    assert (antable.keywords['IATUTC'] == 33.0)
    assert(abs(antable.keywords['E'] - math.e) < 1e-7)
    operator = antable.keywords['OPERATOR']
    assert (operator.strip() == 'NRAO')

finally:
    uvdata.zap()
