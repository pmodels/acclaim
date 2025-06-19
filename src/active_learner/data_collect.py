# This file collects a single data point using the OSU benchmark suite
#   
#   Arguments:
#   $1 = Name of collective
#   $2 = Algorithm to test
#   $3 = Number of nodes
#   $4 = Number of points per node
#   $5 = Message size

import itertools
import numpy as np #type: ignore
import subprocess
import multiprocessing
import sys
import os
import glob
import uuid
import shutil
from datetime import datetime
from src.user_config.config_manager import ConfigManager


# This function uses a Python subprocess to run the microbenchmark script 
def collect_point_runner(name, alg, n, ppn, msg_size, nodefile_path=None):
  n = int(n)
  ppn = int(ppn)
  msg_size = int(msg_size)

  if "_ch4" == name[-4:]:
    runner =ConfigManager.get_instance().get_value('settings', 'ch4_runner')
    name = name[:-4]
  else:
    runner = ConfigManager.get_instance().get_value('settings', 'runner')

  result = subprocess.run([runner,
                           ConfigManager.get_instance().get_value('settings', 'mpich_path'),
                           ConfigManager.get_instance().get_value('settings', 'launcher_path'),
                           ConfigManager.get_instance().get_value('settings', 'osu_path'),
                           "osu_" + name,
                           alg,
                           str(n),
                           str(ppn),
                           str(msg_size),
                           nodefile_path if nodefile_path else ""],
                           check=True, capture_output=True, text=True).stdout
  result = float(result)
  return result

# This function is a wrapper for collect_point_runner that breaks a feature set into parts,
# looking up the alg name, and undoing the preprocessing
def collect_point_single(name, algs, point, nodefile=None):
  alg = algs[point[3]]
  n = 2 ** (point[0] - 1)
  ppn =  2 ** (point[1] - 1)
  msg_size = 2 ** (point[2] - 1)
  return collect_point_runner(name, alg, n, ppn, msg_size, nodefile)


# This function generates a unique directory path so concurrent ACCLAiM do not interfere with each other
def create_unique_directory(root_path):
    # Generate a unique directory name using a timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex
    unique_dir_name = f"{timestamp}_{unique_id}"
    
    # Construct the full path for the unique directory
    unique_dir_path = os.path.join(root_path, "_parallel_nodefiles", unique_dir_name)
    
    # Create the unique directory
    os.makedirs(unique_dir_path, exist_ok=True)
    
    return unique_dir_path

# This function is a wrapper for collect_point_single that collects multiple points in one call
def collect_point_batch(name, algs, points, topo=None):
  print("Attempting to collect: ", points)
  num_results = points.shape[0]
  i = 0
  results = []
  if topo is None:
    for row in points:
      results.append(collect_point_single(name, algs, row))

  else:
    parallel_batch_inputs = []
    root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
    nodefile_dir_path = create_unique_directory(root_path)
    while i < num_results:
      row = points[i,:]
      n = 2 ** (row[0] - 1)
      print("Attempting to fit ", int(n))
      nodes = topo.fit_point(n)
      if(nodes):
        path = os.path.join(nodefile_dir_path, f"nodefile{i}")
        nodefile_path = topo.create_nodefile(nodes, path)
        if nodefile_path:
          parallel_batch_inputs.append((name, algs, row, nodefile_path))
        else:
          parallel_batch_inputs.append((name, algs, row))
        i += 1
        print("Fit passed: ", parallel_batch_inputs[-1])
      else:
        print("Fit failed, collecting ", len(parallel_batch_inputs), " points in parallel")
        print("Collecting points: ", parallel_batch_inputs)
        p = multiprocessing.Pool(processes=len(parallel_batch_inputs))
        outputs = p.starmap(collect_point_single, parallel_batch_inputs)
        p.close()
        p.join()
        for output in outputs:
            results.append(output)
        topo.reset_fit()
        parallel_batch_inputs = []

    if(len(parallel_batch_inputs) != 0):
      print("Collecting leftover points")
      print("Collecting ", len(parallel_batch_inputs), " points in parallel")
      with multiprocessing.Pool(processes=len(parallel_batch_inputs)) as pool:
        outputs = pool.starmap(collect_point_single, parallel_batch_inputs)
      for output in outputs:
        results.append(output)
    topo.reset_fit()
  
    if os.path.isdir(nodefile_dir_path):
        shutil.rmtree(nodefile_dir_path)

  if(len(results) != num_results):
    print("Error, did not collect the right amount of data!")
  return np.asarray(results)        
