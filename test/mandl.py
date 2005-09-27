from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage

AIPS.userno = 1999

image = AIPSImage('MANDELBROT', 'MANDL', 1, 1)
if image.exists():
    image.zap()

mandl = AIPSTask('mandl')
mandl.outdata = image
mandl.imsize[1:] = [ 512, 512 ]
mandl.go()

try:
    header = image.header
    print 'Dimension: %dx%d' % (header.naxis[0], header.naxis[1])
    print image.tables
finally:
    image.zap()
