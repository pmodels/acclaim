# This script sets up the project

import subprocess
import sys
import os

# List of required packages
required_packages = ['numpy', 'sklearn', 'configparser', 'pathlib']

# Function to check if package is installed and attempt to install it if not
def check_and_install_package(package):
    try:
        __import__(package)
        print(f"{package} is installed.")
    except ImportError:
        if package == 'sklearn':
            package = 'scikit-learn'
        print(f"{package} is not installed. Please install {package} and try again.")
        return False

    return True

# Check each package from the list
for package in required_packages:
    if not check_and_install_package(package):
        raise Exception("Missing at least one necessary package.")

# All packages are installed if we reach here
try:
    import configparser
    # Place the generation of config.ini here
    config = configparser.ConfigParser()
    
    config['settings'] = {
        'acclaim_root': os.getcwd()
    }
    
    # Writing the config file to the directory of the script
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("config.ini has been generated.")
    
except Exception as e:
    print(f"An error occurred: {e}")