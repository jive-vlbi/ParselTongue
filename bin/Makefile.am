## Process this file with automake to create Makefile.in.

bin_SCRIPTS = ParselTongue ParselTongueServer

EXTRA_DIST = ParselTongue.in ParselTongueServer.in

# Files that should be removed, but which Automake does not know.
CLEANFILES = $(bin_SCRIPTS)


## ------------- ##
## The scripts.  ##
## ------------- ##

edit = sed \
	-e 's,@datadir\@,$(pkgdatadir),g' \
	-e 's,@PYTHON\@,$(PYTHON),g'

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
