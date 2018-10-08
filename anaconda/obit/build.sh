#!/bin/bash

export LDFLAGS="-L$PREFIX/lib -Wl,-rpath,$PREFIX/lib"

./configure --with-cfitsio=$PREFIX
make
mkdir -p $PREFIX/lib/obit/python
cp ./python/*.so $PREFIX/lib/obit/python
cp ./python/*.py $PREFIX/lib/obit/python
