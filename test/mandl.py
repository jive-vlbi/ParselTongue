from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage

AIPS.userno = 3601
AIPSTask.version = '31DEC05'

name = 'MANDELBROT'
klass = 'MANDL'
disk = 3
seq = 1

mandl = AIPSTask('mandl')
mandl.outname = name
mandl.outclass = klass
mandl.outdisk = disk
mandl.outseq = seq
mandl.imsize = [ 512.0, 512.0 ]
mandl.go()

image = AIPSImage(name, klass, disk, seq)
try:
    header = image.header()
    print 'Dimension: %dx%d' % (header['inaxes'][0], header['inaxes'][1])
    tables = image.tables()
    print tables
finally:
    image.zap()
