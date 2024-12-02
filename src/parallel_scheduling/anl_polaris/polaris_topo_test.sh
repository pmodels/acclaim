#!/bin/bash
#PBS -l select=24:system=polaris
#PBS -l walltime=00:05:00
#PBS -l place=scatter
#PBS -l filesystems=home
#PBS -q prod
#PBS -A MPICH_MCS
#PBS -N polaris-topo-test

#Set up the environment

###Declaring variables
NNODES=`wc -l < $PBS_NODEFILE`

###Directories

#Test

echo "Hi! Im doing the thing!"
echo "Number of Nodes = $NNODES"

cd $PBS_O_WORKDIR

cp $PBS_NODEFILE nodefile.txt

echo "I copied the file, exiting!"
