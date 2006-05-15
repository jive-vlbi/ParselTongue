from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSCat, AIPSImage

AIPS.userno = 1999

print AIPSCat(1)

image = AIPSImage('MANDELBROT', 'MANDL', 1, 1)
if image.exists():
    image.zap()
    pass

try:
    mandl = AIPSTask('mandl')
    mandl.outdata = image
    mandl.imsize[1:] = [ 512, 512 ]
    mandl.go()

    print AIPSCat(1)

finally:
    image.zap()
