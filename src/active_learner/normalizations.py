# This file includes all functions to normalize the input features and benchmarked values

import os
import numpy as np
import copy

from sklearn import preprocessing


########################################################################
# LOG COLUMN
########################################################################

#Take the log of a column
def log_column(data, col_num):
  data[:,col_num] = np.log2(data[:,col_num]) + 1
  return data

#Undoes the log of a column
def undo_log_column(data, col_num):
  data[:,col_num] = 2 ** (data[:,col_num] - 1) 
  return data


########################################################################
# INPUT
########################################################################

#Preprocess features
def preprocess_input(X, norm_type="log"):
  X = X.astype(float)
  
  #For log scaling
  if(norm_type == "log"):
    X = log_column(X, 0)
    X = log_column(X, 1)
    X = log_column(X, 2)
    return X
  #For normal standardization
  if(norm_type == "norm"):
    scaler = preprocessing.StandardScaler().fit(X)
    return scaler.transform(X)
  
  #For no preprocessing
  return X

def undo_preprocess_input(X, norm_type="log"):
  X = X.astype(float)

  #For Log scaling
  if(norm_type == "log"):
    X = undo_log_column(X, 0)
    X = undo_log_column(X, 1)
    X = undo_log_column(X, 2)
    return X

  #For no preprocessing
  return X


########################################################################
# OUTPUT
########################################################################

#Normalize the output data
def normalize_output(y, num_algs, norm_type="log"):
  y = y.astype(float)
  y_nf = copy.deepcopy(y)
  
  #For algorithm normalization
  if(norm_type == "alg"):
    i = 0
    while (i + num_algs - 1) < len(y):
      normal = y[i]
      for x in range(num_algs):
        y[i+x] /= normal
      i += num_algs
    
    #Add log to alg
    y = np.log10(y) + 1
    return y, y_nf
  
  
  #For log normalization
  if(norm_type == "log"):
    y = np.log10(y) + 1
    return y, y_nf

  #For normal standardization
  if(norm_type == "norm"):
    scaler = preprocessing.StandardScaler().fit(np.reshape(y, (-1,1)))
    y = scaler.transform(np.reshape(y, (-1,1))).flatten()
    return y, y_nf

  #For scaling/normalization
  if(norm_type == "scale"):
    min_val = np.amin(y)
    max_val = np.amax(y)
    divide_val = max_val - min_val
    y = (y - min_val)/divide_val
    return y, y_nf

  #For no normalization
  return y, y_nf

#Undo the normalization of output
def undo_normalize_output(X, y_nf, X_set, y_set, num_algs, norm_type="log"):
  y_set = np.asarray(y_set).astype(float)
  y_nf = np.asarray(y_nf).astype(float)
  
  #For algorithm normalization
  if(norm_type == "alg"):
    #Add log to alg
    y_set = 10 ** (y_set - 1)
    
    i = 0
    y_set_nf = []
    for row_set in X_set:
      j = 0
      for row in X:
        if np.all(row[0:3] == row_set[0:3]) and row[3] == 0:
          y_set_nf.append(y_set[i]*y_nf[j])
        j+=1
      i+=1
    
    y_set_nf = np.asarray(y_set_nf)
    return y_set_nf

  #For log normalization
  if(norm_type == "log"):
    y_set_nf = 10 ** (y_set - 1)
    return y_set_nf

  #For normal standardization
  if(norm_type == "norm"):
    scaler = preprocessing.StandardScaler().fit(np.reshape(y_nf, (-1,1)))
    y_set_nf = scaler.inverse_transform(np.reshape(y_set, (-1,1))).flatten()
    return y_set_nf
  
  #For scaling/normalization
  if(norm_type == "scale"):
    min_val = np.amin(y_nf)
    max_val = np.amax(y_nf)
    mult_val = max_val - min_val
    y_set_nf = y_set*mult_val + min_val
    return y_set_nf

  #For no normalization
  return y_set



