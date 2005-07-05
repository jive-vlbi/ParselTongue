from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSImage

AIPS.userno = 3601

image = AIPSImage('MANDELBROT', 'MANDL', 1, 1)

mandl = AIPSTask('mandl')
mandl.outdata = image
mandl.imsize[1:] = [ 64, 64 ]
mandl.go()

try:
    jmfit = AIPSTask('jmfit')
    jmfit.indata = image
    jmfit.ngauss = 4
    jmfit.domax[1:] = [1, 0, 0, 0]
    jmfit.go()
    print 'Peak values:', jmfit.fmax[1:]
finally:
    image.zap()
