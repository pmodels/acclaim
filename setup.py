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
def check_mpich_installation(mpich_path):
    libmpi_path = os.path.join(mpich_path, 'lib', 'libmpi.la')
    mpiexec_path = os.path.join(mpich_path, 'bin', 'mpiexec')
    
    # Check if the lib file exists
    if not os.path.exists(libmpi_path):
        # Throw a FileNotFoundError exception with a message if the file does not exist
        raise FileNotFoundError("MPICH cannot be found at the specified location.")

    # Check if mpiexec exists
    if not os.path.exists(mpiexec_path):
        warnings.warn(("MPICH install found, but mpiexec is not present." 
                        " If you are using a third-party launcher, please refer to the README/documentation"
                        " on how to update the included scripts to work on your system."))
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
parser.add_argument('system', type=str, choices = ['polaris', 'local', 'serial'],
                        help = 'The system to setup for parallel scheduling')
parser.add_argument('max_ppn', type=int, nargs='?',
                        help = 'The maximum processes per node for a single microbenchmark run')

args = parser.parse_args()
mpich_path = args.mpich_path[0]

# Set Max PPN if necessary based on arguments
if args.system == 'polaris':
    max_ppn = 64
elif not args.max_ppn:
    if args.system == 'local':
        max_ppn = 8
    elif args.system == 'serial':
        max_ppn = 64
else:
    max_ppn = args.max_ppn

# Check each required package
for package in required_packages:
    if not check_package(package):
        raise Exception("Missing at least one necessary package.")

# Check MPICH install
check_mpich_installation(mpich_path)

# Download and install the OSU Microbenchmarks
if os.path.exists("osu_microbenchmarks"):
    print("OSU Microbenchmarks already installed!")
else:
    os.makedirs("osu_microbenchmarks")
    print("Installing the OSU Microbenchmarks...")
    subprocess.run(["wget", "https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.5-1.tar.gz"])
    subprocess.run(["mv", "osu-micro-benchmarks-7.5-1.tar.gz", "osu_microbenchmarks"])
    subprocess.run(["tar", "-xzf", "osu_microbenchmarks/osu-micro-benchmarks-7.5-1.tar.gz", "-C", "osu_microbenchmarks", "--strip-components=1"])
    subprocess.run(["cp", "utils/osu/osu_build.sh", "osu_microbenchmarks"])
    mpicc_path = os.path.join(mpich_path, "bin", "mpicc")
    mpicxx_path = os.path.join(mpich_path, "bin", "mpicxx")
    with new_cd('osu_microbenchmarks'):
        subprocess.run(["chmod", "+x", "osu_build.sh"])
        subprocess.run(["./osu_build.sh", mpicc_path, mpicxx_path])
        if os.path.exists("build/libexec/osu-micro-benchmarks/mpi/collective/osu_allreduce"):
            print("OSU Microbenchmarks installed successfully!")
        else:
            raise Exception("Error installing OSU Microbenchmarks.")

# Write the config file
config = configparser.ConfigParser()

config['settings'] = {
    'acclaim_root': os.getcwd(),
    'mpich_path': mpich_path,
    'osu_path': os.path.join(os.getcwd(), "osu_microbenchmarks/build/libexec/osu-micro-benchmarks/mpi/collective"),
    'system': args.system,
    'max_ppn': max_ppn
}

print("Writing the config.ini file...")
with open('config.ini', 'w') as configfile:
    config.write(configfile)
print("config.ini has been generated.")
