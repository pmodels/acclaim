#!/bin/bash
#./scripts/run_test_single_alg.sh $(TEST) $(PATH_TO_TESTS) $(ALG) $(NODE_STRING) $(PPN_STRING) $(MSG_SIZE_STRING)

# Runs a single OSU Benchmark for a single algorithm, returns the data
# $1 = MPICH path
# $2 = osu_microbenchmark path
# $3 = name of test
# $4 = algorithm name
# $5 = number of nodes
# $6 = number of ppn
# $7 = message size
# $8 (optional) = nodefile

mpich_path=$1
osu_path=$2
test_name=$3
alg=$4
n=$5
ppn=$6
msg_size=$7
if [ ! -z "$8" ]; then
  nodefile=$8
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

export MPIR_CVAR_${coll_name_upper}_INTRA_ALGORITHM="$alg"
env_var="MPIR_CVAR_${coll_name_upper}_INTRA_ALGORITHM"

if [ -z "$nodefile" ]; then
    ${mpich_path}/bin/mpiexec -n $processes -ppn $ppn ${osu_path}/${test_name} -m "$msg_size":"$msg_size_plus" | awk -v nodes="$n" -v ppn="$ppn" -v name="$test_name" -v alg=$alg\
        '! /#/ && NF {if($2 != ""){print name"\t"nodes"\t"ppn"\t"alg"\t"$1"\t"$2"\t"$3"\t"$4} else{print name"\t"nodes"\t"ppn"\t"alg"\t1\t"$1}}' \
        | awk -v test="$test_name" -v alg="$alg" -v node="$n" -v proc="$ppn" -v msg_size="$msg_size" '{
            if($1 == test && $2 == node && $3 == proc && $4 == alg && $5 == msg_size){
                total+=$6; 
                count+=1;
            }
        } 
        END {if(count){print total/count}}'
else
    ${mpich_path}/bin/mpiexec -f $nodefile -n $processes -ppn $ppn ${osu_path}/${test_name} -m "$msg_size":"$msg_size_plus" | awk -v nodes="$n" -v ppn="$ppn" -v name="$test_name" -v alg=$alg\
        '! /#/ && NF {if($2 != ""){print name"\t"nodes"\t"ppn"\t"alg"\t"$1"\t"$2"\t"$3"\t"$4} else{print name"\t"nodes"\t"ppn"\t"alg"\t1\t"$1}}' \
        | awk -v test="$test_name" -v alg="$alg" -v node="$n" -v proc="$ppn" -v msg_size="$msg_size" '{
            if($1 == test && $2 == node && $3 == proc && $4 == alg && $5 == msg_size){
                total+=$6; 
                count+=1;
            }
        } 
        END {if(count){print total/count}}'
fi
