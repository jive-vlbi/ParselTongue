# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)

AC_INIT(ParselTongue, 0.92, kettenis@jive.nl)
AM_INIT_AUTOMAKE(1.9)
AC_CONFIG_SRCDIR(python/ParselTongue.py)

## --------- ##
## Scripts.  ##
## --------- ##

AC_CONFIG_FILES(bin/Makefile)

## -------- ##
## Python.  ##
## -------- ##

AM_PATH_PYTHON(2.2)
AC_CONFIG_FILES([python/Makefile python/Proxy/Makefile test/Makefile])

## ------------ ##
## Conclusion.  ##
## ------------ ##

AC_CONFIG_FILES(Makefile)
AC_OUTPUT
