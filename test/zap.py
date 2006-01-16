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
    assert(image.header.datamax == 254.0)
    image.zap_table('PL', -1)
    assert(image.header.datamax == 254.0)
finally:
    image.zap()
