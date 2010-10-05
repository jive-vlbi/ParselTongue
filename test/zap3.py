from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData
from AIPSTV import AIPSTV

import os
import signal
import time
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
fitld()

assert(uvdata.exists())

tv = AIPSTV()

# Wait a bit to make sure the address used by the AIPS TV can be
# reused again.
time.sleep(30)

try:
    tv.start()
    uvplt = AIPSTask('uvplt')
    uvplt.indata = uvdata
    uvplt.dotv = 1
    job = uvplt.spawn()
    time.sleep(20)
    succeed = True
    uvplt.abort(job[0], job[1], sig=signal.SIGKILL)
    try:
        uvdata.zap()
    except:
        succeed = False
        pass

    if succeed:
        assert("Zapping unexpectedly succeeded")
        pass
    if not uvdata.exists():
        assert("Data unexpectedly disappeared")
        pass

finally:
    try:
        uvdata.zap(force=True)
    except:
        pass

    tv.kill()
