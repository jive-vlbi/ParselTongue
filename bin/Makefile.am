## Process this file with automake to create Makefile.in.

bin_SCRIPTS = ParselTongue

EXTRA_DIST = ParselTongue.in

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
