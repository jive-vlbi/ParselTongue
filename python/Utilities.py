# Copyright (C) 2005, 2006 Joint Institute for VLBI in Europe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from AIPS import *
from AIPSTask import *
from AIPSData import *
import sys, re

def rdiskappend(proxyname,remotedisk):
	"""Appends proxyname to the global proxy list, and adds the correct
	(proxyname,remotedisk) pair as an AIPSDisk object in the global disk
	list. Returns the disk index in the AIPS.disks list."""

	# Proxyname is only added to the global proxy list if it isn't already
	# there, of course, and the appropriate entry from AIPS.proxies is used
	# to create an AIPSDisk object and stick it on the end of the AIPS.disks
	# list. We assume that the proxy is specified as a URL with the FQDN,
	# although duplicates won't really cause any huge problems (it's just
	# unsightly).

	i = 0
	proxyfound = False
	for proxy in AIPS.proxies :
		if proxy == proxyname :
			proxyid = i
			proxyfound = True
			break
		i = i + 1

	if not proxyfound :
		AIPS.proxies.append(proxyname)
		proxyid = len(AIPS.proxies) - 1
	
	rdisk = AIPSDisk(AIPS.proxies[proxyid],remotedisk)

	j = 1 # First disk entry in AIPS.disks is always None!
	diskfound = False
	for disk in AIPS.disks[1:] :
		if (rdisk.url == disk.url) and (rdisk.disk == disk.disk) :
			diskid = j
			diskfound = True
			break
		j = j + 1

	if not diskfound :
		AIPS.disks.append(rdisk)
		diskid = len(AIPS.disks) - 1

	return diskid

def rftscopy(AIPSDataSource,AIPSDataTarget):
	"""
	Copies data from one AIPS repository to another on a remote host.
	"""

	# Takes two AIPSData objects as arguments. The first refers to the data
	# store on the local host. The second is a "fake" object that is filled
	# in by rftscopy.  Works by converting first to a FITS file, transporting
	# via ssh, and then importing the result into the remote AIPS client.
	# FITS transport implies a substantial conversion overhead, which is
	# required once on each end, but has the advantage of automatically
	# adjusting to the correct byte-endianness.  If you are quite sure that
	# the remote client is on a machine with the same endian convention, use
	# the rcopy() method instead.

	# The transport step also assumes that an RSA/DSA keypair has been
	# established between client and server to permit SSH logins without a
	# password, and that ssh is available on the user's path (and really,
	# shouldn't it be, here in the 21st century?)

	# write out a temporary FITS file
	fitswrite = AIPSTask('FITTP')
	fitswrite.indata = AIPSDataSource
	# truncate so that outfile is not longer than 48 total
	# characters, due to AIPS being a retarded 70's child...
	inname = fitswrite.inname[0:37]
	outname = "/tmp/" + inname + ".fits"
	fitswrite.outfile = outname
	fitswrite.go()

	# extract the target hostname from the proxy url
	hostpattern = "http://(.*):[0-9]+"
	match = re.search(hostpattern,AIPS.disks[AIPSDataTarget.disk].url)
	rhost = match.group(1)
	command_string = "scp " + outname + " " + rhost + ":/tmp"
	os.system(command_string)

	# and import the temporary FITS file at the other end
	fitsimport = AIPSTask('FITLD')
	fitsimport.infile = outname
	fitsimport.outdata = AIPSDataTarget
	fitsimport.go()

	# clean up /tmp on both machines
	os.remove(outname)
	returnval = os.system("ssh " + rhost + " rm " + outname)
	# os.system return values are encoded in the same way as those of
	# os.wait(): 16-bits, with the low 8 encoding the signal number, if any,
	# and the high 8 encoding the return value of the command
	if (returnval >> 8) != 0 :
		print "Unable to remove temporary file from the remote filesystem."
	return 0

