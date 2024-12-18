#!/bin/bash

# This script builds and installs the OSU microbenchmarks

mpicc=$1
mpicxx=$2

pwd=$(pwd)
./configure --prefix=${pwd}/build CC=$mpicc CXX=$mpicxx
make
make install
