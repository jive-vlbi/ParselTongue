#!/bin/bash

./configure --prefix=$PREFIX
make shared
make install
