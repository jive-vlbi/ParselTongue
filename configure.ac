# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.57)

AC_INIT(ParselTongue, 1.1, sipior@jive.nl)
AM_INIT_AUTOMAKE(1.6)
AC_CONFIG_SRCDIR(python/ParselTongue.py)

## --------- ##
## Scripts.  ##
## --------- ##

AC_CONFIG_FILES(bin/Makefile)

## -------- ##
## Python.  ##
## -------- ##

AM_PATH_PYTHON(2.2)
AC_CONFIG_FILES([python/Makefile python/Proxy/Makefile
                 python/Wizardry/Makefile test/Makefile])

## ------ ##
## Obit.  ##
## ------ ##

OBIT_PYTHONPATH=
AC_ARG_WITH(obit,
            AC_HELP_STRING([--with-obit=DIR],
                           [search for Obit in DIR]),
            [if test -f "$withval/python/Obit.py"; then
    OBIT_PYTHONPATH="$withval/python"; export ac_obit_pythonpath
  fi[]])
AC_CACHE_CHECK([for Obit], [ac_cv_obit],
               [
cat <<_ACEOF >conftest.py
try:
    import OSystem, OErr
except:
    print "missing"
else:
    print "found"
_ACEOF
PYTHONPATH=$PYTHONPATH:$OBIT_PYTHONPATH; export PYTHONPATH
ac_cv_obit=`$PYTHON conftest.py 2>/dev/null`
])
if test "$ac_cv_obit" != found; then
  AC_MSG_ERROR([Obit is not available])
fi
AC_SUBST(OBIT_PYTHONPATH)

## -------- ##
## NumPy.   ##
## -------- ##

AC_ARG_WITH(numpy,
            AC_HELP_STRING([--with-numpy],
                           [use NumPy instead of numarray]),
            [],
            [with_numpy=no])

AC_CACHE_CHECK([for numpy], [ac_cv_numpy],
               [
cat <<_ACEOF >numpytest.py
try:
    import numpy
except:
    print "missing"
else:
    print "found"
_ACEOF
ac_cv_numpy=`$PYTHON numpytest.py 2>/dev/null`
])

if test "$ac_cv_numpy" != found; then
  AC_MSG_ERROR([NumPy is not available])
fi

if test "$with_numpy" = yes -a "$ac_cv_numpy" = found; then
cd python/Wizardry
patch -b<<_ACEOF
--- AIPSData.py	2008-08-26 03:29:09.000000000 +0200
+++ AIPSData_numpy.py	2008-08-26 13:40:13.000000000 +0200
@@ -24,7 +24,7 @@
 
-# Fail gracefully if numarray isn't available.
+# Fail gracefully if NumPy isn't available.
 try:
-    import numarray
+    import numpy
 except:
-    numarray = None
+    numpy = None
     pass
@@ -419,4 +419,4 @@
         # Give an early warning we're not going to succeed.
-        if not numarray:
-            msg = 'Numerical Python (numarray) not available'
+        if not numpy:
+            msg = 'Numerical Python (NumPy) not available'
             raise NotImplementedError, msg
@@ -464,4 +464,5 @@
         shape = len(self._data.VisBuf) / 4
-        self._buffer = numarray.array(sequence=self._data.VisBuf,
-                                      type=numarray.Float32, shape=shape)
+        self._buffer = numpy.array(sequence=self._data.VisBuf,
+                                      type=numpy.float32)
+        self._buffer = self._buffer.reshape(shape)
         self._first = self._data.Desc.Dict['firstVis'] - 1
@@ -469,3 +470,3 @@
         count = InfoList.PGet(self._data.List, "nVisPIO")[4][0]
-        self._buffer.setshape((count, -1))
+        self._buffer.shape = (count, -1)
         self._index = 0
@@ -537,3 +538,3 @@
         shape = (inaxes[3], inaxes[2], inaxes[1], inaxes[0])
-        visibility.setshape(shape)
+        visibility.shape = shape
         return visibility
@@ -922,4 +923,5 @@
         shape = tuple(shape)
-        pixels = numarray.array(sequence=self._data.PixBuf,
-                                type=numarray.Float32, shape=shape)
+        pixels = numpy.array(sequence=self._data.PixBuf,
+                                type=numpy.float32)
+        pixels = pixels.reshape(shape)
         self._dirty = True
_ACEOF
cd ../..
fi

## ------------ ##
## Conclusion.  ##
## ------------ ##

AC_CONFIG_FILES([Makefile doc/Makefile])
AC_OUTPUT
