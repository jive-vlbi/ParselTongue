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
    image.rename('APPLE')
    assert(image.exists())
    assert(AIPSImage('APPLE', 'MANDL', 1, 1).exists())
    assert(not AIPSImage('MANDELBROT', 'MANDL', 1, 1).exists())
    image.rename(seq = 8)
    assert(image.exists())
    assert(image.seq == 8)
    image.rename(klass='APPLE', seq=99)
    assert(image.exists())
    image.rename(klass='PEAR', seq=0)
    assert(image.exists())
    assert(image.seq != 0)
    image.rename('MANDLEBROT', seq=1)
    assert(image.exists())
    try:
        image.rename('MANDLEBROT', seq=1)
    except:
        pass
    else:
        raise AssertionError("Rename unexpectedly succeeded")
finally:
    image.zap()
