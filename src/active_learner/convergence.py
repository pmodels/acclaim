# This file contains all functions to deal with model convergence

import os
import csv
import numpy as np

#This function checks whether a model has converged
def convergence_criteria(convergence_vals):
  #default criteria is four consecutive values within .001
  threshold = .001
  if(abs(convergence_vals[-1] - convergence_vals[-2]) > threshold):
    return False
  if(abs(convergence_vals[-2] - convergence_vals[-3]) > threshold):
    return False
  if(abs(convergence_vals[-3] - convergence_vals[-4]) > threshold):
    return False

  return True



