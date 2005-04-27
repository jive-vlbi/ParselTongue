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

This module provides a simple XML-RPC server that can run classic AIPS
tasks and provide verb-like access to AIPS data on a machine.

"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
import Proxy.AIPSData
import Proxy.AIPSTask

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ServerFuncs:
    def __init__(self):
        self.AIPSUVData = Proxy.AIPSData.AIPSUVData()
        self.AIPSImage = Proxy.AIPSData.AIPSImage()
        self.AIPSTask = Proxy.AIPSTask.AIPSTask()

server = SimpleXMLRPCServer(('', 8000))
server.register_instance(ServerFuncs())
server.serve_forever()


