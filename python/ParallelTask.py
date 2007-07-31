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

	pass                                # class ParallelTask

