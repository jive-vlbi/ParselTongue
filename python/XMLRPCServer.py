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


