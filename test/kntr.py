import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage
from AIPSTV import AIPSTV

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
fitld.infile = file
fitld.outdata = image
fitld.msgkill = 2
fitld.go()

try:
    env = os.environ.copy()
    env['TVDEV'] = 'TVDEV01'
    env['TVDEV01'] = 'sssin:localhost'

    file = env['LOAD'] + '/TVSERV.EXE'
    lock_pid = os.spawnve(os.P_NOWAIT, file, ['TVSERVER'], env)
    file = env['LOAD'] + '/XAS'
    server_pid = os.spawnve(os.P_NOWAIT, file, ['XAS'], env)

    kntr = AIPSTask('kntr')
    kntr.indata = image
    kntr.docont = 0
    kntr.dovect = 0
    kntr.dotv = 1
    kntr.go()

    tv = AIPSTV()
    tv.kill()

    os.waitpid(lock_pid, 0)
    os.waitpid(server_pid, 0)

finally:
    image.zap()
