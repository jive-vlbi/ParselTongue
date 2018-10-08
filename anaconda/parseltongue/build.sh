#!/bin/bash

./configure --prefix=$PREFIX --with-obit=$PREFIX/lib/obit
make
make install
