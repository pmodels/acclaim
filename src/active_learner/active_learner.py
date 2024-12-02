# This file performs active learning using jackknife variance
#   

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from src.active_learner.utils import preprocess_features, unprocess_features
from src.active_learner.initialization import create_feature_space, get_initial_points
from src.active_learner.algs import read_algs, add_algs, get_all_algs
from src.active_learner.point_selection import point_selection_single
from src.active_learner.data_collect import collect_point_batch
from src.active_learner.normalizations import normalize_output, undo_normalize_output, undo_preprocess_input
from src.active_learner.jackknife import jackknife
from src.active_learner.convergence import convergence_criteria
from src.parallel_scheduling.anl_theta.anl_theta_parallel_scheduling import Topology, gen_topology, get_topology

#Our target machine, Theta, schedules based on nodes not processes. Therefore, the hardware has a constant number of ppn regardless of what we are testing
MACHINE_PPN = 64

def train_model(n, ppn, msg_size, collective, min_reps=10, theta=0):

  #Preprocess the input values and generate the feature space
  new_n, new_ppn, new_msg_size = preprocess_features(n, ppn, msg_size)
  feature_space = create_feature_space(new_n, new_ppn, new_msg_size, collective)

  #read algs into a dictionary, initialize X and Y arrays
  algs = read_algs(collective)
  X = add_algs(feature_space, algs)
  X_train = None
  y_train = None
  y_train_nf = None

  #initialize variables
  first = True
  converged = False
  convergence_vals = []
  y = None
  rf = None
    
  #initialize topology
  num_processes=n*MACHINE_PPN
  topo_file = gen_topology(num_processes)
  topo = get_topology(topo_file)

  ######################################################
  #
  # TRAINING MODEL W/ ACTIVE LEARNING
  #
  ######################################################
  while not (converged):

    #
    # STEP 1: SELECT TRAINING POINTS AND COLLECT DATA
    #

    #If it is the first iteration, train for default initial points
    if(first):
      #Select inital training points
      initial_points = get_initial_points(feature_space)

      #Add all algorithms
      X_train = add_algs(initial_points, algs)
      
      print("Done initializing")

      #Collect the data
      new_points_y = collect_point_batch(collective, algs, X_train, theta, topo)

      print("Done collecting first data")

      #Process the results, create y_train/y_train_nf
      y_train, y_train_nf = normalize_output(new_points_y, len(algs.keys()), norm_type="alg")

      print("First iteration complete")
      first = False

    #Otherwise, use uncertainty calculations to determine the next point  
    else:
      #Calculate uncertainty and select a point
      new_point_x, new_point_index = point_selection_single(rf, X_train, X)
      
      #Retrieve all algorithm versions of the point (all other inputs/features are the same)
      new_points_x = get_all_algs(new_point_x, algs)

      #Append to X_train
      X_train = np.vstack([X_train, new_points_x])

      #Collect the data
      new_points_y = collect_point_batch(collective, algs, new_points_x, theta, topo)
     
      #Process the results, append to y_train/y_train_nf
      new_y_train, new_y_train_nf = normalize_output(new_points_y, len(algs.keys()), norm_type="alg")
      y_train = np.append(y_train, new_y_train)
      y_train_nf = np.append(y_train_nf, new_y_train_nf)

    #
    # STEP 2: TRAIN THE MODEL
    #
    
    #create moodel and fit it to the data
    rf = RandomForestRegressor()
    rf = rf.fit(X_train, y_train)

    #
    # STEP 3: CHECK FOR CONVERGENCE
    #

    #collect convergence data
    convergence_vals.append(jackknife(rf, X))

    if(len(convergence_vals) < min_reps):
      continue
    else:
      if(convergence_criteria(convergence_vals)):
        converged = True
 
  return feature_space, rf







