#!/bin/bash

# Runs a single OSU Benchmark for a single algorithm, returns the latency
# $1 = MPICH path
# $2 = Process launcher (e.g., mpiexec) path 
# $3 = osu_microbenchmark path
# $4 = name of test
# $5 = algorithm name
# $6 = number of nodes
# $7 = number of ppn
# $8 = message size
# $9 (optional) = nodefile

split_string() {
    local input="$1"
    local alg_name_var="$2"
    local alg_param_var="$3"

    # Use regex to check if the string ends with a number
    if [[ $input =~ ^(.*[^0-9])([0-9]+)$ ]]; then
        # Extract the preceding string and the number
        eval "$alg_name_var='${BASH_REMATCH[1]}'"
        eval "$alg_param_var='${BASH_REMATCH[2]}'"
    else
        # If no number is found, return the whole string and an empty string
        eval "$alg_name_var='$input'"
        eval "$alg_param_var=''"
    fi
}

mpich_path=$1
launcher_path=$2
osu_path=$3
test_name=$4
alg=$5
n=$6
ppn=$7
msg_size=$8

if [ ! -z "$9" ]; then
  nodefile=$9
else
  nodefile=""
fi

let msg_size_plus=$msg_size+1

if [[ $msg_size == 1 ]] ; then
  let msg_size_plus-=1
fi

processes=$(($n*$ppn))

if [[ $processes -lt 2 ]] ; then
  continue
fi

coll="$test_name"
coll_name=${coll:4}
coll_name_upper=$(echo "$coll_name" | tr '[:lower:]' '[:upper:]')

if [ "$alg" == "smp" ] ; then
  continue
fi

alg_name=""
alg_param=""
split_string "$alg" alg_name alg_param

if [[ $alg_name ==  "alpha" ]]; then
      export MPIR_CVAR_${coll_name_upper}__COMPOSITION=1
fi
if [[ $alg_name ==  "beta" ]]; then
      export MPIR_CVAR_${coll_name_upper}__COMPOSITION=2
fi
if [[ $alg_name ==  "gamma" ]]; then
      export MPIR_CVAR_${coll_name_upper}__COMPOSITION=3
fi
if [[ $alg_name ==  "delta" ]]; then
      export MPIR_CVAR_${coll_name_upper}__COMPOSITION=4
fi

# echo ${launcher_path} -f $nodefile -n $processes -ppn $ppn -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH ${osu_path}/${test_name} -m "$msg_size":"$msg_size_plus"

if [ -z "$nodefile" ]; then
    ${launcher_path} -n $processes -ppn $ppn -genv MPIR_CVAR_DEVICE_COLLECTIVES=all -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH ${osu_path}/../../../../../c/get_local_rank ${osu_path}/${test_name} -d sycl -m "$msg_size":"$msg_size_plus"

else
    ${launcher_path} --hostfile $nodefile -n $processes -ppn $ppn -genv MPIR_CVAR_DEVICE_COLLECTIVES=all -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH ${osu_path}/../../../../../c/get_local_rank ${osu_path}/${test_name} -d sycl -m "$msg_size":"$msg_size_plus"

fi