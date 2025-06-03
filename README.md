# ACCLAiM: MPI Collective Autotuning for Exascale

Welcome! ACCLAiM is a tool that autotunes MPICH's collective algorithm selection at allocation time.
The goal of ACCLAiM is to transparently improve the performance of large-scale HPC workloads.

## Dependencies

* Python3 (Tested with v3.13)
	* numpy (Tested with v2.1.3)
 	* scikit-learn (Tested with v1.5.2)
	* configparser (Tested with v1.3.1)
	* pathlib (Tested with v1.01)  
* [MPICH](https://github.com/pmodels/mpich) (Tested with v4.3.0) 
	* For install instructions, see the MPICH README
* OSU Microbenchmarks (Tested with v7.5.1)
	* Installed automatically by `setup.py`	

## Setup

To setup the ACCLAiM tool, run the provided setup script `setup.py` with the following arguments:
- **`<mpich_path>`**: The path to the MPICH installation directory
- **`<system_type>`**: The type of system used for parallel scheduling. The following options are available:
  - `polaris` for ANL's Polaris system
  - `aurora` for ANL's Aurora system
  - `serial` disables the parallel scheduler (recommended for all other systems)
  - `local` allows an infinite number of parallel microbenchmarks. Use for testing purposes only.
- **`[--max_ppn]`** (optional): The maximum number of processes per node for a single microbenchmark run.
- **`[--num_initial_points]`** (optional): The number of data points ACCLAiM should randomly sample at the beginning of exploration. We generally recommend against changing this value!
- **`[--convergence_threshold]`** (optional): The threshold that cumulative jackknife variance must be under for consecutive iterations to exit. We generally recommend against changing this value!
- **`[--timeout]`** (optional): The maximum number of minutes before training should exit, even if it has not met the convergence threshold.
- **`[--launcher_path]`** (optional): The path to the process launcher (e.g., mpiexec). If this argument is not supplied, ACCLAiM will use ${mpich_path}/bin/mpiexec.

Note: The `max_ppn` argument is optional. The provided value will be ignored for `system=polaris`.
For `local`, the default is 8, and for `serial`, the default is 64. 

`setup.py` checks for all required Python packages and will fail if they are not detected.
If this occurs, install the requested package and re-run the script.
If using a virtual environment, you can easily install all the necessary Python packages by running `pip install -r requirements.txt`.

When it completes successfully, `setup.py` creates `config.ini` at the root directory of your repository.
Review all of the settings and confirm they are correct.

## Using ACCLAiM

### Description

ACCLAiM currently supports tuning for all blocking, regular collectives that have more than one algorithm implemented in MPICH: MPI_Allgather, MPI_Allreduce, MPI_Alltoall, MPI_Bcast, MPI_Reduce, and MPI_Reduce_scatter.

ACCLAiM is an *allocation-time* autotuner, meaning it is invoked in an HPC jobscript (submitted through a workload manager such as SLURM) just before the application is invoked using `mpiexec`.
Examples are included at the bottom of this section.

ACCLAiM includes 3 `make` commands to perform tuning:
- **`gen_config_single`**: Tunes a single specified collective
- **`gen_config_multiple`**: Tunes a list of specified collectives.
- **`gen_config_all`**: Tunes all supported collectives. Note that this command is not recommended; instead, profile your application using a tool such as [mpiP](https://github.com/LLNL/mpiP) and only tune the most common collectives in your workload.

These commands have the following shared arguments:
- **`N`**: Maximum number of nodes (i.e., number of nodes in the job).
- **`PPN`**: Maximum number of processes per node (i.e., number of processes per node used in the job).
- **`MSG_SIZE`**: Largest collective message size to tune. For the best tuning results, we recommend a large size, e.g., 1048576, even if the application only uses small messages. On the other hand, unless you are running at very large scale, setting the max message size to few MBs is enough to find the optimal selections. The selection logic is straightforward once you hit the bandwidth bounds of the network.
- **`SAVE_FILE`**: The location to store the tuned .json file created by ACCLAiM. We recommend creating a separate directory for these tuning files and using the job ID in the name, so simultaneous jobs do not overwrite each other's files.

`gen_config_single` and `gen_config_multiple` have additional arguments to select the collective(s) to tune:
- **`COLLECTIVE`** (`gen_config_single`): Collective to tune. Specify the collective in all lower case without the `MPI` prefix, e.g., "allreduce" or "reduce_scatter".
- **`COLLECTIVE_LIST`** (`gen_config_multiple`): List of collectives to tune. Specify the collectives in a comma-separated list using all lower case without the `MPI` prefix, e.g., "allreduce,reduce_scatter,bcast".

These arguments are passed by name following the `make` command.
To understand how to run these commands, please inspect the `Makefile` and see the examples below.

### Applying the Tuning File

To instruct MPICH to use the new tuning file, pass the path to the file using the `MPIR_CVAR_COLL_SELECTION_TUNING_JSON_FILE` environment variable.

### Examples
Tuning MPI_Allreduce on ANL Aurora:
```
NNODES=`wc -l < $PBS_NODEFILE`
PPN=12
PROCS=$(($NNODES * $PPN))

APP_DIR=$(pwd)
ACCLAIM_PATH=path/to/acclaim

cd $ACCLAIM_PATH
mkdir -p tuning_jsons

save_file_path=${ACCLAIM_PATH}/tuning_jsons/${PBS_JOBID}.json
make gen_config_single N=$NNODES PPN=$PPN MSG_SIZE=1048576 COLLECTIVE="allreduce" SAVE_FILE="${save_file_path}"

cd $APP_DIR
mpiexec \
    -n $PROCS \
    -ppn $PPN \
    -genv MPIR_CVAR_COLL_SELECTION_TUNING_JSON_FILE=${save_file_path} \
    ...
```

Tuning MPI_Allreduce and MPI_Bcast on ANL Aurora:
```
NNODES=`wc -l < $PBS_NODEFILE`
PPN=12
PROCS=$(($NNODES * $PPN))

APP_DIR=$(pwd)
ACCLAIM_PATH=path/to/acclaim

cd $ACCLAIM_PATH
mkdir -p tuning_jsons

save_file_path=${ACCLAIM_PATH}/tuning_jsons/${PBS_JOBID}.json
make gen_config_multiple N=$NNODES PPN=$PPN MSG_SIZE=1048576 COLLECTIVE_LIST="allreduce,bcast" SAVE_FILE="${save_file_path}"

cd $APP_DIR
mpiexec \
    -n $PROCS \
    -ppn $PPN \
    -genv MPIR_CVAR_COLL_SELECTION_TUNING_JSON_FILE=${save_file_path} \
    ...
```

Tuning all collectives on ANL Aurora:
```
NNODES=`wc -l < $PBS_NODEFILE`
PPN=12
PROCS=$(($NNODES * $PPN))

APP_DIR=$(pwd)
ACCLAIM_PATH=path/to/acclaim

cd $ACCLAIM_PATH
mkdir -p tuning_jsons

save_file_path=${ACCLAIM_PATH}/tuning_jsons/${PBS_JOBID}.json
make gen_config_all N=$NNODES PPN=$PPN MSG_SIZE=1048576 SAVE_FILE="${save_file_path}"

cd $APP_DIR
mpiexec \
    -n $PROCS \
    -ppn $PPN \
    -genv MPIR_CVAR_COLL_SELECTION_TUNING_JSON_FILE=${save_file_path} \
    ...
```

## Known Issues

When installing the OSU microbenchmarks on Mac systems, there may be a compilation error because Mac OS does not implement pthreads barrier.
To work around this issue, We have successfully compiled the benchmarks by adding an implementation to `osu_microbenchmarks/c/util/osu_util_mpi.h/c.
See [this patch](https://github.com/pmwkaa/ioarena/commit/b8854d4b164591cb62a97f67a6dc3645b26f4b39#diff-32028cf20b50afd839db7008666a051ba761b4947f1690445f42bda23705c96bR37) for an example implementation.

## Publication

ACCLAiM is the result of [this paper](https://mjwilkins.org/assets/pdfs/acclaim.pdf). Please check it out for more details.

To refer to ACCLAiM, please use the following citation:
```
@inproceedings{acclaim,
  author={Wilkins, Michael and Guo, Yanfei and Thakur, Rajeev and Dinda, Peter and Hardavellas, Nikos},
  booktitle={2022 IEEE International Conference on Cluster Computing (CLUSTER)}, 
  title={ACCLAiM: Advancing the Practicality of MPI Collective Communication Autotuning Using Machine Learning}, 
  year={2022},
  pages={161-171},
  doi={10.1109/CLUSTER51413.2022.00030}
}
```
