"""

This module provides instances to dispatch function calls locally,
without doing any RPC.

"""

# The AIPSTask module should always be available.
import Proxy.AIPSTask
AIPSTask = Proxy.AIPSTask.AIPSTask()

# The same goes for the ObitTask module.
import Proxy.ObitTask
ObitTask = Proxy.ObitTask.ObitTask()

# The AIPSData module depends on Obit.  Since Obit might not be
# available, leave out the AIPSUVData and AIPSImage instances if we
# fail to load the module.
try:
    import Proxy.AIPSData
except:
    pass
else:
    AIPSImage = Proxy.AIPSData.AIPSImage()
    AIPSUVData = Proxy.AIPSData.AIPSUVData()
