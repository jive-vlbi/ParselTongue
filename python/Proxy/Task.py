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

This module provides bits and pieces to implement generic Task proxy
objects.

"""

# Generic Python stuff.
import fcntl, os, pty, select, signal

class Task:
    def __init__(self):
        self._pid = {}

    def spawn(self, path, args, env=None):
        """Start the task."""

        (pid, tid) = pty.fork()
        if pid == 0:
            try:
                if env:
                    os.execve(path, args, env)
                else:
                    os.execv(path, args)
            finally:
                os._exit(1)
        else:
            fcntl.fcntl(tid, fcntl.F_SETFL, os.O_NONBLOCK)
            self._pid[tid] = pid
            return tid

    def finished(self, tid):
        """Check whether the task has finished."""
        return self._pid[tid] == 0

    def messages(self, tid):
        """Return task's messages."""

        (iwtd, owtd, ewtd) = select.select([tid], [], [], 0.25)
        if tid in iwtd:
            try:
                messages = os.read(tid, 1024)
                if len(messages) > 0:
                    messages = messages.split('\r\n')
                    return [msg for msg in messages if msg]
            except:
                pass

            pass

        # If reading failed, it's (probably) because the child
        # process died.
        (pid, status) = os.waitpid(self._pid[tid], os.WNOHANG)
        if pid:
            assert(pid == self._pid[tid])
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                self._pid[tid] = 0
        return []

    def feed(self, tid, banana):
        """Feed the task."""

        os.write(tid, banana)
        pass

    def wait(self, tid):
        """Wait for the task to finish."""

        assert(self.finished(tid))

        del self._pid[tid]
        os.close(tid)
        return

    def abort(self, tid, sig=signal.SIGINT):
        """Abort a task."""

        os.kill (self._pid[tid], sig)

        del self._pid[tid]
        os.close(tid)
        return
