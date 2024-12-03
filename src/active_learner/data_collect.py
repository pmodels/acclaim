# This file collects a single data point using the OSU benchmark suite
#   
#   Arguments:
#   $1 = Name of collective
#   $2 = Algorithm to test
#   $3 = Number of nodes
#   $4 = Number of points per node
#   $5 = Message size

import itertools
import numpy as np
import subprocess
import multiprocessing
import sys
import os
import glob
from src.parallel_scheduling.anl_polaris.anl_polaris_parallel_scheduling import Topology, create_nodefile
from src.user_config.config_manager import ConfigManager

# This function uses a Python subprocess to run the benchmark script 
def collect_point(name, alg, n, ppn, msg_size):
  #print(name, alg, n, ppn, msg_size)
  n = int(n)
  ppn = int(ppn)
  msg_size = int(msg_size)
  print("Lower-level collecting point:",name,alg,n,ppn,msg_size)
  result = subprocess.run(["./src/active_learner/collect_point_single.sh", name, alg, str(n), str(ppn), str(msg_size)], check=True, capture_output=True, text=True).stdout
  result = float(result)
  print("Finished lower-level collecting point:",name,alg,n,ppn,msg_size)
  return result

# This function is the same as the previous but runs a different script that sets a custom nodefile for parallel tests
def collect_point_nodefile(name, alg, n, ppn, msg_size, path):
  #print(name, alg, n, ppn, msg_size, path)
  n = int(n)
  ppn = int(ppn)
  msg_size = int(msg_size)
  print("Lower-level collecting point nodefile:",name,alg,n,ppn,msg_size,path)
  result = subprocess.run(["./src/active_learner/collect_point_single_nodefile.sh", name, alg, str(n), str(ppn), str(msg_size), path], check=True, capture_output=True, text=True).stdout
  result = float(result)
  print("Finished lower-level collecting point:",name,alg,n,ppn,msg_size)
  return result

# This function is a wrapper for collect_point that takes care of breaking a feature set into parts, looking up the alg name, and undoing the preprocessing
def collect_point_single(name, algs, point, path=None):
  alg = algs[point[3]]
  n = 2 ** (point[0] - 1)
  ppn =  2 ** (point[1] - 1)
  msg_size = 2 ** (point[2] - 1)
  if path:
    return collect_point_nodefile(name, alg, n, ppn, msg_size, path)
  else:
    return collect_point(name, alg, n, ppn, msg_size)


# This function is a wrapper for collect_point_single that collects multiple points in one call
# If parallel=1, use machine-specific point to safely execute in parallel
def collect_point_batch(name, algs, points, parallel=0, topo=None):
  print("Attempting to collect: ", points)
  num_results = points.shape[0]
  i = 0
  results = []
  if(not parallel):
    for row in points:
      results.append(collect_point_single(name, algs, row))

  elif(parallel):
    parallel_batch_inputs = []
    root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
    while i < num_results:
      row = points[i,:]
      n = 2 ** (row[0] - 1)
      print("Attempting to fit ", n)
      nodes = topo.fit_point(n)
      if(nodes):
        path = f"{root_path}/parallel_nodefiles/nodefile{i}"
        create_nodefile(nodes, path)
        parallel_batch_inputs.append((name, algs, row, path))
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

    files = glob.glob(f"{root_path}/parallel_nodefiles/*")
    for f in files:
      os.remove(f)

    if(len(parallel_batch_inputs) != 0):
      print("Collecting leftover points")
      print("Collecting ", len(parallel_batch_inputs), " points in parallel")
      with multiprocessing.Pool(processes=len(parallel_batch_inputs)) as pool:
        outputs = pool.starmap(collect_point_single, parallel_batch_inputs)
      for output in outputs:
        results.append(output)
    topo.reset_fit()

  if(len(results) != num_results):
    print("Error, did not collect the right amount of data!")
  return np.asarray(results)        
