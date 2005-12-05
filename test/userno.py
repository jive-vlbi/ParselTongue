from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage

AIPS.userno = 1999

image = AIPSImage('MANDELBROT', 'MANDL', 1, 1)
if image.exists():
    image.zap()

image2 = AIPSImage('MANDELBROT', 'MANDL', 1, 1, 2)
if image2.exists():
    image2.zap()

mandl = AIPSTask('mandl')
mandl.userno = 2
mandl.outdata = image
mandl.imsize[1:] = [ 512, 512 ]
mandl.go()

try:
    assert(not image.exists())
    assert(image2.exists())

    AIPS.userno = 2
    image = AIPSImage('MANDELBROT', 'MANDL', 1, 1)
    assert(image.exists())
finally:
    image2.zap()
