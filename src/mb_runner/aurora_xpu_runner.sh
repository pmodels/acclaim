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

export MPIR_CVAR_${coll_name_upper}_INTRA_ALGORITHM="$alg_name"
if [[ -n $alg_param ]]; then
    if [[ $alg_name ==  "recexch" || $alg_name == "recexch_doubling" || $alg_name == "recexch_halving" ]]; then
      export MPIR_CVAR_${coll_name_upper}_RECEXCH_KVAL="$alg_param"
    fi
    if [[ $alg_name ==  "tree" ]]; then
      export MPIR_CVAR_${coll_name_upper}_TREE_KVAL="$alg_param"
    fi
    if [[ $alg_name ==  "recursive_multiplying" ]]; then
      export MPIR_CVAR_${coll_name_upper}_RECURSIVE_MULTIPLYING_KVAL="$alg_param"
    fi
    if [[ $alg_name ==  "k_brucks" ]]; then
      export MPIR_PARAM_${coll_name_upper}_BRUCKS_KVAL="$alg_param"
    fi

fi

# echo ${launcher_path} -f $nodefile -n $processes -ppn $ppn -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH ${osu_path}/${test_name} -m "$msg_size":"$msg_size_plus"

if [ -z "$nodefile" ]; then
    ${launcher_path} -n $processes -ppn $ppn -genv MPIR_CVAR_DEVICE_COLLECTIVES=none -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH /home/wilkins/osu_microbenchmarks_sycl/c/get_local_rank ${osu_path}/${test_name} -d sycl -m "$msg_size":"$msg_size_plus" | awk -v nodes="$n" -v ppn="$ppn" -v name="$test_name" -v alg=$alg\
        '! /#/ && NF {if($2 != ""){print name"\t"nodes"\t"ppn"\t"alg"\t"$1"\t"$2"\t"$3"\t"$4} else{print name"\t"nodes"\t"ppn"\t"alg"\t1\t"$1}}' \
        | awk -v test="$test_name" -v alg="$alg" -v node="$n" -v proc="$ppn" -v msg_size="$msg_size" '{
            if($1 == test && $2 == node && $3 == proc && $4 == alg && $5 == msg_size){
                total+=$6; 
                count+=1;
            }
        } 
        END {if(count){print total/count}}'
else
    ${launcher_path} --hostfile $nodefile -n $processes -ppn $ppn -genv MPIR_CVAR_DEVICE_COLLECTIVES=none -genv LD_LIBRARY_PATH=${mpich_path}/lib:$LD_LIBRARY_PATH /home/wilkins/osu_microbenchmarks_sycl/c/get_local_rank ${osu_path}/${test_name} -d sycl -m "$msg_size":"$msg_size_plus" | awk -v nodes="$n" -v ppn="$ppn" -v name="$test_name" -v alg=$alg\
        '! /#/ && NF {if($2 != ""){print name"\t"nodes"\t"ppn"\t"alg"\t"$1"\t"$2"\t"$3"\t"$4} else{print name"\t"nodes"\t"ppn"\t"alg"\t1\t"$1}}' \
        | awk -v test="$test_name" -v alg="$alg" -v node="$n" -v proc="$ppn" -v msg_size="$msg_size" '{
            if($1 == test && $2 == node && $3 == proc && $4 == alg && $5 == msg_size){
                total+=$6; 
                count+=1;
            }
        } 
        END {if(count){print total/count}}'
fi