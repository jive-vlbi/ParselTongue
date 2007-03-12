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

"""
This module acts as a container for AIPSTask objects, and is responsible for
farming out jobs in parallel to a cluster whose individual nodes run XML-RPC
servers. Assumptions inherent in the current implementation:

	1. All data has been copied to disks visible to the remote AIPS client,
	and are present in the appropriate AIPS disk catalogue. This currently
	also implies that the remote node has been chosen for each job prior to
	insertion in the parallel queue.

	2. An XML-RPC server must already be running on each of the intended
	computational nodes. (duh)

	3. Transport of files is performed via ssh's RSA/DSA authentication,
	which necessitates a keypair and a valid .authorized_hosts file on each
	cluster node.
"""

from Task import Task

class ParallelTask(Task):
	"""Our container class for AIPSTask objects. Also contains methods for
	despatching and monitoring tasks, a la the go() method in AIPSTask"""

	proxy_list = [] # this list of available URLs must be manually set atm
	proxy_index = 0 # points to the next available proxy

	def __init__(self):
		self.tasklist = []
		self.current = -1  # index of last task to be despatched

	def queue(self,task):
		try:
			if !(isinstance(task,AIPSTask)):
				raise TypeError
		except TypeError:
			print 'Argument is not an AIPSTask'
			return
		else:
			self.tasklist.append(task)
			return len(self.tasklist)

	def runnext(self):
		"""
		Run the next member of the task queue.
		"""
		self.current += 1
		self.tasklist[current].go()
		return

	def runqueue(self):
		"""
		Run the remainder of the task queue.
		"""
		while self.current <= len(self.tasklist) :
			self.current += 1
			self.tasklist[current].go()
		return

	def rftcopy(self,inname1,inclass1,inseq1,indisk1,intype1,rhost):
		"""
		Copies data from one AIPS repository to another on the remote rhost,
		by converting first to a FITS file, transporting via ssh, and then
		importing the result into the remote AIPS client. FITS transport
		implies a substantial conversion overhead, which is required once on
		each end, but has the advantage of automatically adjusting to the
		correct byte-endianness.  If you are quite sure that the remote
		client is on a machine with the same endian convention, use the
		rcopy() method instead.

		The transport step also assumes that an RSA/DSA keypair has been
		established between client and server to permit SSH logins without a
		password.
		"""
		
		# N.B. parameters to specify source and destination files:
		# two sets of INNAME, INCLASS, INSEQ, INDISK, INTYPE

		fitswrite = AIPSTask('FITTP')
		fitswrite.inname = inname1
		fitswrite.inclass = inclass1
		fitswrite.inseq = inseq1
		fitswrite.indisk = indisk1
		fitswrite.intype = intype1
		if len(inname1) > 37 :
			# truncated so that outfile is not longer than 48 total
			# characters, due to AIPS being a retarded 70's child...
			inname1 = inname1[0:37]
		outname = "/tmp/" + inname1 + ".fits"
		fitswrite.outfile = "'" + outname # again with the retarded AIPS

		command_string = "scp " + outname + " " + rhost + ":/tmp"
		os.system(command_string)
		fitsimport = AIPSTask('FITLD')
		import_data_into_aips_via_xmlrpc()
		return


	pass                                # class ParallelTask
