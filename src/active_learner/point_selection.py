# This file performs an uncertainty test using jackknife and selects training points
#   
#   Arguments:
#   $1 = pre-trained random forest regressor
#   $2 = train set X values
#   $3 = test set X values
#   $4 = (for batch only) batch size

import csv
import numpy as np
import sys

from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestRegressor

from src.active_learner.jackknife import jackknife_variances

def point_selection_single(regressor, X_train, X_test):

  variances = jackknife_variances(regressor, X_test)
  new_point_index = np.argmax(variances)
  new_point = X_test[new_point_index,:]
  
  #if(np.any(np.all(np.isin(X_train, new_point), axis=1))):
  #  print("Warning: selecting stale point")

  return new_point, new_point_index

def point_selection_batch(regressor, X_train, X_test, batch_size):

  variances = jackknife_variances(regressor, X_test)
  new_point_indices = np.argpartition(variances, -batch_size)[-batch_size:]
  new_points =  X_test[new_point_indices,:]
  
  return new_points, new_point_indices

