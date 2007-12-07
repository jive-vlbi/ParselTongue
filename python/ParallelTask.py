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
	and are present in the appropriate AIPS disk catalogue.

	2. An XML-RPC server must already be running on each of the intended
	computational nodes. (duh)
"""

import os, sys
from Task import Task
from AIPSTask import AIPSTask

class ParallelTask(Task):
	"""Our container class for AIPSTask objects. Also contains methods for
	despatching and monitoring tasks, a la the go() method in AIPSTask"""

	def __init__(self):
		Task.__init__(self)
		self._tasklist = []
		self._current = 0  # index of last task to be despatched

	def queue(self,task):
		try:
			if not isinstance(task,AIPSTask):
				raise TypeError
		except TypeError:
			print 'Argument is not an AIPSTask'
			return
		else:
			self._tasklist.append(task)
			return len(self._tasklist)

	def runnext(self,next=1):
		"""
		Run next number of jobs in the task queue
		"""
		try:
			if (self._current + next) > len(self._tasklist) :
				raise IndexError
		except IndexError:
			print "Error in runnext:",
			print "run queue has fewer than %d tasks remaining." % next
			return
		while next > 0 :
			if (os.fork()) == 0 :
				self._tasklist[self._current].go()
				sys.exit(0)
			self._current += 1
			next -= 1
		return

	def runqueue(self):
		"""
		Run the remainder of the task queue.
		"""
		while self._current < len(self._tasklist) :
			if (os.fork()) == 0 :
				self._tasklist[self._current].go()
				sys.exit(0)
			self._current += 1
		return

	pass                                # class ParallelTask
