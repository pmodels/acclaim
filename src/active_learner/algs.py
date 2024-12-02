# This file contains all functions to deal with algorithms for a given collective

import os
import csv
import numpy as np

#This function finds all algorithms and returns in an enumerated dictionary
def read_algs(collective):
  root_path = os.environ.get('ROOT')
  algs_path = root_path + '/utils/mpich/algorithm_config/all_algs.csv'

  with open(algs_path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    algs_dict = None
    for row in csv_reader:
      if row:
        if row[0] == collective:
          algs = row[1:]
          if 'smp' in algs: algs.remove('smp')
          keys = range(len(algs))
          algs_dict = dict(zip(keys, algs))
      
  if(algs_dict == None):
    print("Warning: Collective Not Found!")
  return algs_dict

#This function takes a 2D array of input args for the ML model and adds algorithms as another feature
def add_algs(feature_space, algs):

  num_algs = len(list(algs.keys()))
  if(np.squeeze(feature_space).ndim == 1):
    alg_space = np.zeros((num_algs, feature_space.size + 1))
    for j in range(num_algs):
      index = j
      alg_space[index,:-1] = feature_space
      alg_space[index,-1] = j

  else:
    alg_space = np.zeros((feature_space.shape[0]*num_algs, feature_space.shape[1]+1))
    for i in range(feature_space.shape[0]):
      for j in range(num_algs):
        index = i*num_algs + j
        alg_space[index,:-1] = feature_space[i,:]
        alg_space[index,-1] = j
  
  return alg_space


#This function takes a set of input args and returns all possible algorithms for that input
def get_all_algs(x, algs):

  num_algs = len(list(algs.keys()))
  new_points_x = np.zeros((num_algs, x.shape[0]))

  i = 0
  for key in algs.keys():
    new_points_x[i,:-1] = x[:-1]
    new_points_x[i,-1] = key
    i+=1

  return new_points_x






