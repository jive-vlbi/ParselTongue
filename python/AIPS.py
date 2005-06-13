"""

This module provides the AIPSDisk and AIPS classes.  Together they
provide some basic infrastructure used by the AIPSTask and AIPSData
modules.

"""

# Generic Python stuff.
import os

# Available proxies.
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

    # List of available proxies.
    proxies = [ LocalProxy ]

    # AIPS disk mapping. 
    disks = [ None ]                    # Disk numbers are one-based.

    # Who will ever need more than 9 AIPS disks?    
    for disk in xrange(1, 10):
        area = 'DA%02d' % disk
        if not area in os.environ:
            break
        disks.append(AIPSDisk(None, disk))
        continue

    # Message log.
    log = None
