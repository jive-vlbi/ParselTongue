import LocalProxy
from xmlrpclib import ServerProxy

class AIPSDisk:
    
    """Class representing a (possibly remote) AIPS disk.  An instance
       of this class stores an AIPS disk number and the URL of the
       proxy through which it can be accessed.  For local AIPS disks
       the URL will be None."""

    def __init__(self, url, disk):
        self.url = url
        self.disk = disk

    def proxy(self):
        """Return the proxy through which this AIPS disk can be
           accessed."""
        if self.url:
            return ServerProxy(self.url)
        else:
            return LocalProxy

class AIPS:
    
    """Container for several AIPS-related default values."""

    # Default AIPS user ID.
    userno = 0

    # AIPS disk mapping. 
    disks = [ None,                      # Disk numbers are one-based.
              AIPSDisk(None, 1),
              AIPSDisk(None, 2),
              AIPSDisk('http://localhost:8000', 1),
              AIPSDisk('http://localhost:8000', 2) ]

    # List of available proxies.
    proxies = [ LocalProxy, ServerProxy('http://localhost:8000') ]
