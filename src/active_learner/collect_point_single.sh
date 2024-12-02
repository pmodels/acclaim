#!/bin/bash
#./scripts/run_test_single_alg.sh $(TEST) $(PATH_TO_TESTS) $(ALG) $(NODE_STRING) $(PPN_STRING) $(MSG_SIZE_STRING)

# Runs a single OSU Benchmark for a single algorithm, returns the data
# $1 = name of test
# $2 = algorithm name
# $3 = number of nodes
# $4 = number of ppn
# $5 = message size

tests_path="$ROOT/ml-mpitune-osu-benchmarks/osu-micro-benchmarks-5.6.3/build/libexec/osu-micro-benchmarks/mpi/collective/"
script_path=$(pwd)
osu_path="$ROOT/benchmarking/osu_benchmarks"

cd $osu_path
./scripts/run_parse_single_alg.sh "osu_$1" $tests_path $2 $3 $4 $5
cd $script_path
