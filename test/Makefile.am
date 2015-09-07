## Process this file with automake to create Makefile.in.

check_SCRIPTS = ParselTest

TESTS = msglog.py \
	cat.py mandl.py imean.py jmfit.py fitld.py fitld2.py kntr.py \
	convenience.py flag.py history.py history2.py indxr.py keywords.py \
	keywords2.py keywords3.py pixels.py userno.py \
	visibilities.py visibilities2a.py visibilities2b.py \
	visibilities3.py visibilities4.py visibilities5.py \
	uvcon.py zap.py zap2.py zap3.py zap4.py \
	$(top_srcdir)/python/MinimalMatch.py \
	$(top_srcdir)/python/Task.py \
	$(top_srcdir)/python/AIPSTask.py \
	$(top_srcdir)/python/AIPSData.py
TESTS_ENVIRONMENT = ./ParselTest

EXTRA_DIST = $(TESTS) template.py ParselTest.in VLBA1.UVCON

# Files that should be removed, but which Automake does not know.
CLEANFILES = $(check_SCRIPTS)

## ------------- ##
## The scripts.  ##
## ------------- ##

edit = sed \
	-e 's,@top_srcdir\@,$(top_srcdir),g' \
	-e 's,@PYTHON\@,$(PYTHON),g' \
	-e 's,@OBIT_PYTHONPATH\@,$(OBIT_PYTHONPATH),g'

## All the files below depend on Makefile so that they are rebuilt
## when prefix etc. changes.
## Use chmod -w to prevent people from editing the wrong file by accident.
ParselTest: $(srcdir)/ParselTest.in Makefile
	rm -f ParselTest ParselTest.tmp
	$(edit) $(srcdir)/ParselTest.in >ParselTest.tmp
	chmod +x ParselTest.tmp
	chmod -w ParselTest.tmp
	mv -f ParselTest.tmp ParselTest
