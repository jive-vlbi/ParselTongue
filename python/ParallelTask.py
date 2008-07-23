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
import AIPSTask
import AIPS

class ParallelTask :
    proxy = None
    tid = None
    finished = 0
    def __init__(self,task) :
        self.task = task

    def spawn(popsnum) :
        pass

class ParallelQueue :
    """
    Our container class for ParallelTask objects. Also contains methods for
    despatching and monitoring tasks.
    """

    def __init__(self):
        self._tasklist = []
        self._current = 0  # index of last task to be despatched

    def queue(self,task):
        try:
            if not isinstance(task,AIPSTask.AIPSTask):
                raise TypeError
        except TypeError:
            print 'Argument is not an AIPSTask'
            return
        else:
            self._tasklist.append(ParallelTask(task))
            return len(self._tasklist)

    def finished(self):
        """Returns True if any queued task has completed"""

        anydone = False
        for task in self._tasklist :
            if (task.task.finished(task.proxy,task.tid)) :
                task.finished = True
                anydone = True
        return anydone

    def runqueue(self):
        """
        Run the remainder of the task queue.
        """
        while self._current < len(self._tasklist) :
            (proxy,tid) = self._tasklist[self._current].task.spawn()
            self._tasklist[self._current].proxy = proxy
            self._tasklist[self._current].tid = tid
            self._current += 1
        while len(self._tasklist) > 0 :
            self.queuewait()
        return

    def queuewait(self) :
        while not self.finished() :
            for task in self._tasklist :
                message = task.task.messages(task.proxy,task.tid)
                if (message) : 
                    for note in message :
                        task.task._log.write('%s\n' % note)
                        continue
                    task.task._log.flush()
        else :
            j = len(self._tasklist) - 1
            while (j >= 0) : 
                if (self._tasklist[j].finished == True) :
                    self._tasklist[j].task.wait(self._tasklist[j].proxy,self._tasklist[j].tid)
                    del self._tasklist[j]
                j = j - 1
        return

    def listqueue(self,verbose=1):
        """
        Display the remaining queued tasks
        """
        index = self._current
        while index < len(self._tasklist) :
            print "AIPS task %s" % self._tasklist[index].task._name
            for adverb in self._tasklist[index].task._input_list :
                if self._tasklist[index].task.__dict__[adverb] == '':
                    print "    '%s': ''" % adverb
                else:
                    value = AIPSTask.PythonList(self._tasklist[index].task.__dict__[adverb])
                    print "    '%s': %s" % (adverb, value)
                    pass
                continue
            index += 1
        return

    pass                                # class ParallelTask
