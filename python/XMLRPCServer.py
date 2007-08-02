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

This module provides a simple XML-RPC server that can run classic AIPS
tasks and provide verb-like access to AIPS data on a machine.

"""

import sys
import xmlrpclib
# Stolen shamelessly from Thomas Bellman, on the Python-list, June 2006.
# WARNING: Dirty hack below.
# Replace the dumps() function in xmlrpclib with one that by default
# handles None, so SimpleXMLRPCServer can return None.
class _xmldumps(object):
	def __init__(self, dumps):
		self.__dumps = (dumps,)
	def __call__(self, *args, **kwargs):
		kwargs.setdefault('allow_none', 1)
		return self.__dumps[0](*args, **kwargs)
xmlrpclib.dumps = _xmldumps(xmlrpclib.dumps)

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

# Global AIPS defaults.
import AIPS

# Import AIPS modules.
import Proxy.AIPSTask
import Proxy.AIPSData

class XMLRPCServer(SimpleXMLRPCServer):
    allow_reuse_address = True
    pass

class ServerFuncs:
    def __init__(self):
        self.AIPSTask = Proxy.AIPSTask.AIPSTask()
        self.AIPSUVData = Proxy.AIPSData.AIPSUVData()
        self.AIPSImage = Proxy.AIPSData.AIPSImage()
        self.AIPSCat = Proxy.AIPSData.AIPSCat()
        return

    def _dispatch(self, name, args):
        # For security reasons, SimpleXMLRPCServer in Python
        # 2.3.5/2.4.1, no longer resolves names with a dot in it.  Se
        # here we explicitly accept names starting with 'AIPS' and
        # containing a single dot; that should be safe enough.
        if name.startswith('AIPS') and name.count('.') == 1:
            name = name.split('.')
            inst = getattr(self, name[0])
            method = getattr(inst, name[1])
            return method(*args)
        msg = "object has no attribute '%s'" % name
        raise AttributeError, msg

    pass                                # class ServerFuncs

# This bit of unpleasantness comes about from the ugly hack that is the
# _xmldumps class above. Python 2.5 supports the "allow_none" attribute for
# SimpleXMLRPCServer objects, whereas Python 2.1 t/m 2.4 require the
# _xmldumps redefinition above. However, these versions will break if
# "allow_none" is passed to the constructor, and the _xmldumps hack doesn't
# work with Python 2.5. So...
if sys.hexversion >= 0x020500f0 :
	server = XMLRPCServer(('', 8000), allow_none = 1)
else :
	server = XMLRPCServer(('', 8000))

if __name__ == "__main__" :
	server.register_instance(ServerFuncs())
	server.serve_forever()
