from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData

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
    num_tables = len(uvdata.tables)
    uvdata.zap_table('NX', 1)
    assert(len(uvdata.tables) == num_tables - 1)
    indxr = AIPSTask('indxr')
    indxr.indata = uvdata
    indxr()
    assert(len(uvdata.tables) == num_tables)
    
    uvdata = WAIPSUVData(uvdata)
    uvdata.zap_table('NX', 1)
    assert(len(uvdata.tables) == num_tables - 1)
    indxr = AIPSTask('indxr')
    indxr.indata = uvdata
    indxr()
    assert(len(uvdata.tables) == num_tables)

finally:
    uvdata.zap()
