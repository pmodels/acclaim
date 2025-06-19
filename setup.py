# This script sets up the project

import subprocess
import os
import argparse
import warnings
import contextlib
import configparser

###############
### HELPERS ###
###############

# Function to check if MPICH is installed at the provided path
def check_mpich_installation(args, mpich_path):
    libmpi_path_1 = os.path.join(mpich_path, 'lib', 'libmpi.so')
    libmpi_path_2 = os.path.join(mpich_path, 'lib', 'libmpi.la')
    mpiexec_path = os.path.join(mpich_path, 'bin', 'mpiexec')
    
    # Check if the lib file exists
    if not os.path.exists(libmpi_path_1) and not os.path.exists(libmpi_path_2):
        # Throw a FileNotFoundError exception with a message if the file does not exist
        raise FileNotFoundError("MPICH cannot be found at the specified location.")

    # Check if mpiexec exists
    if not os.path.exists(mpiexec_path):
        if not args.launcher_path:
            raise FileNotFoundError("mpiexec not found in MPICH installation and --launcher_path not set!")
    else:
        print("MPICH is properly installed.")

# List of required packages
required_packages = ['numpy', 'sklearn', 'configparser', 'pathlib']

# Function to check if package is installed
def check_package(package):
    try:
        __import__(package)
        print(f"{package} is installed.")
    except ImportError:
        if package == 'sklearn':
            package = 'scikit-learn'
        print(f"{package} is not installed. Please install {package} and try again.")
        return False

    return True

# Context Manager for temporarily changing directories
@contextlib.contextmanager
def new_cd(x):
    d = os.getcwd()
    os.chdir(x)

    try:
        yield

    finally:
        os.chdir(d)

###################
### MAIN SCRIPT ###
###################

# Parse script arguments
parser = argparse.ArgumentParser(description='Setup the ACCLAiM project.')
parser.add_argument('mpich_path', type=str, nargs=1, 
                        help = 'The path to the MPICH install directory')
parser.add_argument('system', type=str, choices = ['polaris', 'aurora_cpu', 'aurora_xpu', 'local', 'serial'],
                        help = 'The system to setup for parallel scheduling')
parser.add_argument('--max_ppn', type=int, nargs='?',
                        help = 'The maximum processes per node for a single microbenchmark run')
parser.add_argument('--num_initial_points', type=int, nargs='?', default=3,
                        help = '''The number of training points to collect in the first iteration. 
                        Increase for fewer algorithms, reduce for many algorithms. Default = 3''')
parser.add_argument('--convergence_threshold', type=float, nargs='?', default=0.0000000015,
                        help = '''The threshold for maximum convergence value over four consecutive 
                        active learning iterations to successfully exit the active learning process. Default = .001.
                        Higher values will exit sooner with potentially less-accurate tuning. Lower values will take longer 
                        to exit but provide more accurate results.''')
parser.add_argument('--timeout', type=int, nargs='?', default=30,
                        help = '''The maximum amount of time in MINUTES before the training process should terminate,
                        even if it has not yet met the convergence criteria. Default = 30''')
parser.add_argument('--launcher_path', type=str,
                        help = 'The path to the process launcher (if not ${mpich_path}/mpiexec)')

args = parser.parse_args()
mpich_path = args.mpich_path[0]

# Set Max PPN if necessary based on arguments
if not args.max_ppn:
    if args.system == 'polaris':
        max_ppn = 64 # The most common PPN for CPU-based workloads on Polaris is 64
    elif args.system == 'aurora_xpu':
        max_ppn = 12 # The most common PPN on Aurora XPU is 12 (1 process per GPU Tile)
    elif args.system == 'aurora_cpu':
        max_ppn = 96 # The most common PPN for CPU-based workloads on Aurora is 96
    elif not args.max_ppn:
        if args.system == 'local':
            max_ppn = 8
        elif args.system == 'serial':
            max_ppn = 64
else:
    max_ppn = args.max_ppn

# Set the launcher path if necessary based on arguments
if args.launcher_path:
    launcher_path = args.launcher_path
else:
    launcher_path = os.path.join(mpich_path, 'bin', 'mpiexec')

# Check each required package
for package in required_packages:
    if not check_package(package):
        raise Exception("Missing at least one necessary package.")

# Check MPICH install
check_mpich_installation(args, mpich_path)

# Download and install the OSU Microbenchmarks
if os.path.exists("osu_microbenchmarks"):
    print("OSU Microbenchmarks already installed!")
else:
    # Download the microbenchmarks or clone them from Github
    os.makedirs("osu_microbenchmarks")
    print("Installing the OSU Microbenchmarks...")
    if args.system == 'aurora_xpu':
        subprocess.run(["git", "clone", "https://github.com/mjwilkins18/aurora_osu_microbenchmarks.git", "osu_microbenchmarks"])
    else:
        subprocess.run(["wget", "https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.5-1.tar.gz"])
        subprocess.run(["mv", "osu-micro-benchmarks-7.5-1.tar.gz", "osu_microbenchmarks"])
        subprocess.run(["tar", "-xzf", "osu_microbenchmarks/osu-micro-benchmarks-7.5-1.tar.gz", "-C", "osu_microbenchmarks", "--strip-components=1"])
    
    # Copy in the correct build script
    if args.system == 'aurora_cpu':
        subprocess.run(["cp", "utils/osu/osu_build_aurora.sh", "osu_microbenchmarks/osu_build.sh"])
    elif args.system == 'aurora_xpu':
        subprocess.run(["cp", "utils/osu/osu_build_aurora_xpu.sh", "osu_microbenchmarks/osu_build.sh"])
    else:
        subprocess.run(["cp", "utils/osu/osu_build.sh", "osu_microbenchmarks/osu_build.sh"])

    # Run the build script
    mpicc_path = os.path.join(mpich_path, "bin", "mpicc")
    mpicxx_path = os.path.join(mpich_path, "bin", "mpicxx")
    with new_cd('osu_microbenchmarks'):
        subprocess.run(["chmod", "+x", "osu_build.sh"])
        subprocess.run(["./osu_build.sh", mpicc_path, mpicxx_path])
        if os.path.exists("build/libexec/osu-micro-benchmarks/mpi/collective/osu_allreduce"):
            print("OSU Microbenchmarks installed successfully!")
        else:
            raise Exception("Error installing OSU Microbenchmarks.")

# Set the system-specific runner script if necessary
runner = os.path.join(os.getcwd(), "src/mb_runner/generic_runner.sh")
ch4_runner = os.path.join(os.getcwd(), "src/mb_runner/generic_runner_ch4.sh")
if args.system == 'aurora_xpu':
    runner = os.path.join(os.getcwd(), "src/mb_runner/aurora_xpu_runner.sh")
    ch4_runner = os.path.join(os.getcwd(), "src/mb_runner/aurora_xpu_runner_ch4.sh")

# Create the temporary directory for nodefiles
nodefile_dir = os.path.join(os.getcwd(), "_parallel_nodefiles")

if not os.path.exists(nodefile_dir):
    os.makedirs(nodefile_dir)

# Write the config file
config = configparser.ConfigParser()

# Select the algorithms csv
if args.system == 'aurora_cpu' or args.system == 'aurora_xpu':
    algs_json = os.path.join(os.getcwd(), "utils/mpich/algorithm_config/all_algs_param_aurora.csv")
else:
    algs_json = os.path.join(os.getcwd(), "utils/mpich/algorithm_config/all_algs_param.csv")

config['settings'] = {
    'acclaim_root': os.getcwd(),
    'mpich_path': mpich_path,
    'launcher_path': launcher_path,
    'osu_path': os.path.join(os.getcwd(), "osu_microbenchmarks/build/libexec/osu-micro-benchmarks/mpi/collective"),
    'runner': runner,
    'ch4_runner': ch4_runner,
    'system': args.system,
    'max_ppn': max_ppn,
    'convergence_threshold': args.convergence_threshold,
    'num_initial_points': args.num_initial_points,
    'timeout': args.timeout,
    'algs_json': algs_json,
}

print("Writing the config.ini file...")
with open('config.ini', 'w') as configfile:
    config.write(configfile)
print("config.ini has been generated.")
