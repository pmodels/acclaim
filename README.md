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

## Setup

To setup the ACCLAiM tool, run the provided setup script `setup.py` with the following arguments:
- **`<mpich_path>`**: The path to the MPICH installation directory
- **`<system_type>`**: The type of system used for parallel scheduling. The following options are available:
  - `polaris` for ANL's Polaris system
  - `aurora` for ANL's Aurora system
  - `serial` disables the parallel scheduler (recommended for all other systems)
  - `local` allows an infinite number of parallel microbenchmarks. Use for testing purposes only.
- **`[max_ppn]`** (optional): The maximum number of processes per node for a single microbenchmark run.
- **`[--launcher_path]`** (optional): The path to the process launcher (e.g., mpiexec). If this argument is not supplied, ACCLAiM will use ${mpich_path}/bin/mpiexec.

Note: The `max_ppn` argument is optional. The provided value will be ignored for `system=polaris`.
For `local`, the default is 8, and for `serial`, the default is 64.

`setup.py` checks for all required Python packages and will fail if they are not detected.
If this occurs, install the requested package and re-run the script.

When it completes successfully, `setup.py` creates `config.ini` at the root directory of your repository.
Review all of the settings and confirm they are correct.

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
