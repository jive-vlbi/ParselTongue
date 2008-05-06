## Process this file with automake to create Makefile.in.

bin_SCRIPTS = ParselTongue ParselTongueServer ParselFileServer TVServer

EXTRA_DIST = ParselTongue.in ParselTongueServer.in ParselFileServer.in TVServer

# Files that should be removed, but which Automake does not know.
CLEANFILES = ParselTongue ParselTongueServer ParselFileServer


## ------------- ##
## The scripts.  ##
## ------------- ##

edit = sed \
	-e 's,@datadir\@,$(pkgdatadir),g' \
	-e 's,@VERSION\@,$(VERSION),g' \
	-e 's,@PYTHON\@,$(PYTHON),g' \
	-e 's,@OBIT_PYTHONPATH\@,$(OBIT_PYTHONPATH),g'

## All the files below depend on Makefile so that they are rebuilt
## when prefix etc. changes.
## Use chmod -w to prevent people from editing the wrong file by accident.
ParselTongue: $(srcdir)/ParselTongue.in Makefile
	rm -f ParselTongue ParselTongue.tmp
	$(edit) $(srcdir)/ParselTongue.in >ParselTongue.tmp
	chmod +x ParselTongue.tmp
	chmod -w ParselTongue.tmp
	mv -f ParselTongue.tmp ParselTongue

ParselTongueServer: $(srcdir)/ParselTongueServer.in Makefile
	rm -f ParselTongueServer ParselTongueServer.tmp
	$(edit) $(srcdir)/ParselTongueServer.in >ParselTongueServer.tmp
	chmod +x ParselTongueServer.tmp
	chmod -w ParselTongueServer.tmp
	mv -f ParselTongueServer.tmp ParselTongueServer

ParselFileServer: $(srcdir)/ParselFileServer.in Makefile
	rm -f ParselFileServer ParselFileServer.tmp
	$(edit) $(srcdir)/ParselFileServer.in >ParselFileServer.tmp
	chmod +x ParselFileServer.tmp
	chmod -w ParselFileServer.tmp
	mv -f ParselFileServer.tmp ParselFileServer
