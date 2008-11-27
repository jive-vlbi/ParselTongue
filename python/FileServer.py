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
This server provides a simple/stupid way to transfer files to /tmp on a
remote machine, without troubling with pesky user authentication &cet.

"""

import os
import sys
import SocketServer

class FileServer(SocketServer.ForkingMixIn, SocketServer.TCPServer) : pass

class FileWriter(SocketServer.BaseRequestHandler) :
    dir = "/tmp"
    def handle(self) :
        copy = open(os.tempnam(self.dir),"w")
        self.request.send(copy.name)
        while True:
            data = self.request.recv(65536)
            if not data : break
            copy.write(data)
        copy.close()

if __name__ == "__main__" :
    try :
        if (len(sys.argv) > 1) :
            server = FileServer(('',8001),FileWriter(sys.argv[1]))
        else :
            server = FileServer(('',8001),FileWriter)
        server.serve_forever()
    except(KeyboardInterrupt) :
        print "FileServer exiting. Later!"
