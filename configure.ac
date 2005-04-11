# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)

AC_INIT(ParselTongue, 0.93, kettenis@jive.nl)
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

## ----- ##
## Obit. ##
## ----- ##

OBIT_PYTHONPATH=
AC_ARG_WITH(obit,
            AC_HELP_STRING([--with-obit=DIR],
                           [search for Obit in DIR]),
            [if test -f "$withval/python/Obit.py"; then
    OBIT_PYTHONPATH="$withval/python"; export ac_obit_pythonpath
  fi[]])
AC_SUBST(OBIT_PYTHONPATH)

## ------------ ##
## Conclusion.  ##
## ------------ ##

AC_CONFIG_FILES([Makefile doc/Makefile])
AC_OUTPUT
