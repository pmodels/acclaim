#!/bin/bash

# This script builds and installs the OSU microbenchmarks

mpicc=$1
mpicxx=$2

pwd=$(pwd)
autoreconf -fi # Aurora has an older version of autoconf/automake than OSU (1.15 vs. 1.16), so we force the reconf to workaround this
./configure --prefix=${pwd}/build CC=$mpicc CXX=$mpicxx
make
make install
