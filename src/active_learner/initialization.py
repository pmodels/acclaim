# This file includes functions to initialize FACT

import numpy as np
from src.user_config.config_manager import ConfigManager


# This function creates the input matrix (X) based on the maximum feature values
def create_feature_space(n, ppn, msg_size, collective):  
  shape_x = n*ppn*msg_size - msg_size #remove one message size to avoid n = 1, ppn = 1 cases
  if "reduce" in collective: #If the collective is a reduction, we must avoid message sizes of 1 and 2, so we reduce the size of the space
    shape_x -= n*ppn*2
    shape_x += 2 #add two back in because we removed n = 1, ppn = 1, msg_size = 1/2 twice
  to_return = np.zeros(shape=(shape_x,3))

  i = 0
  for cur_n in range(n):  
    for cur_ppn in range(ppn):
      if(cur_n == 0 and cur_ppn == 0):
        continue
      for cur_msg_size in range(msg_size):
        if "reduce" in collective and cur_msg_size < 2:
          continue
        to_return[i] = [cur_n + 1, cur_ppn + 1, cur_msg_size + 1]
        i+=1
  
  return to_return


# This function selects initial training points to begin the active learning process
def get_initial_points(X):
  num_points = X.shape[0]
  num_initial_points = int(ConfigManager.get_instance().get_value('settings', 'num_initial_points'))
  if(num_points < num_initial_points):
    return X
  
  # Select the points. We use +2 in the linspace and then remove the largest 2 indices later to
  # skew the select points towards smaller message sizes, which are quicker to collect.
  indices = np.floor(np.linspace(0, num_points - 1, num=num_initial_points + 2))
  indices = indices.astype(int)
  indices = indices[:-2] 
  return X[indices,:]

