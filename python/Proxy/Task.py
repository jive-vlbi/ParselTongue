"""

This module provides bits and pieces to implement generic Task proxy
objects.

"""

# Generic Python stuff.
import fcntl, os, select, pty

class Task:
    def __init__(self):
        self._pid = {}

    def spawn(self, path, args, env=None):
        """Start the task."""

        (pid, tid) = pty.fork()
        if pid == 0:
            if env:
                os.execve(path, args, env)
            else:
                os.execv(path, args)
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
                return os.read(tid, 1024)
            except:
                # If reading failed, it's (probably) because the child
                # process died.
                (pid, status) = os.waitpid(self._pid[tid], os.WNOHANG)
                assert(pid == self._pid[tid])
                if os.WIFEXITED(status) or os.WIFSIGNALLED(status):
                    self._pid[tid] = 0
        return ""

    def wait(self, tid):
        """Wait for the task to finish."""

        assert(self.finished(tid))

        del self._pid[tid]
        os.close(tid)
