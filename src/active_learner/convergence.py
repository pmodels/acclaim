# This file contains all functions to deal with model convergence

import os
import csv
import numpy as np
from src.user_config.config_manager import ConfigManager

#This function checks whether a model has converged
def convergence_criteria(convergence_vals):

  threshold = float(ConfigManager.get_instance().get_value('settings', 'convergence_threshold'))
  if(abs(convergence_vals[-1] - convergence_vals[-2]) > threshold):
    return False
  if(abs(convergence_vals[-2] - convergence_vals[-3]) > threshold):
    return False
  if(abs(convergence_vals[-3] - convergence_vals[-4]) > threshold):
    return False

  return True



