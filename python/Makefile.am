## Process this file with automake to create Makefile.in.

SUBDIRS = Proxy Wizardry

pythonlibdir = $(pkgdatadir)/python
dist_pythonlib_PYTHON = \
	MinimalMatch.py Task.py \
	AIPS.py AIPSUtil.py AIPSTask.py AIPSData.py AIPSTV.py \
	AIPSLite.py \
	FITS.py FITSData.py \
	ObitTask.py \
	LocalProxy.py XMLRPCServer.py FileServer.py \
	ParselTongue.py ptcompleter.py ParallelTask.py Utilities.py
pythonlib_DATA = ptversion.py

EXTRA_DIST = ptversion.py.in

# Files that should be removed, but which Automake does not know.
CLEANFILES = ptversion.py

edit = sed -e 's,@VERSION\@,$(VERSION),g'

## The file below depends on Makefile so that they are rebuilt when
## the version changes.
## Use chmod -w to prevent people from editing the wrong file by accident.
ptversion.py: $(srcdir)/ptversion.py.in Makefile
	rm -f ptversion.py ptversion.tmp
	$(edit) $(srcdir)/ptversion.py.in >ptversion.tmp
	chmod -w ptversion.tmp
	mv -f ptversion.tmp ptversion.py
