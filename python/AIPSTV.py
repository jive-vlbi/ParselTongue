# Copyright (C) 2005 Joint Institute for VLBI in Europe
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

This module provides the AIPSTV class.  This class makes it possible
to control the AIPS TV from Python.

"""

# Generic Python stuff.
import socket, struct


class AIPSTV(object):
    def __init__(self, host='localhost'):
        self.host = host
        self.port = socket.getservbyname('sssin', 'tcp')
        return

    def _send(self, opcode, dat1=0, dat2=0, dat3=0, dat4=0):
        """Send command to the TV server."""
        s = struct.pack('!6h', opcode, dat1, dat2, dat3, dat4, 0)
        self._socket.send(s)
        if opcode == 12:
            return
        s = self._socket.recv(4)
        (status,) = struct.unpack('!h2x', s)
        if status:
            msg = "AIPS TV returned %d", status
            raise IOError, msg
        return

    def _open(self):
        """Open connection to the TV server."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))
        self._send(11)
        return

    def _close(self):
        """Close connection to the TV server."""
        self._socket.send(struct.pack('!6h', 12, 0, 0, 0, 0, 0))
        self._socket.close()
        return

    def clear(self):
        """Init the TV server."""
        self._open()
        self._send(15)
        self._close()
        return

    def kill(self):
        """Close down the TV server."""
        self._open()
        self._socket.send(struct.pack('!6h', 18, 0, 0, 0, 0, 0))
        self._socket.close()
        return

    pass                                # Class AIPSTV
