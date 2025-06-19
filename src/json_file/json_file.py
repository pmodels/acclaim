# This file includes methods to generate a custom .json file to configure MPICH

import sys
import json
import numpy as np
from src.active_learner.algs import read_algs, add_algs
from src.user_config.config_manager import ConfigManager
from src.json_file.param_algs_to_json import split_param_alg, get_param_rules
from collections import OrderedDict

# Custom exception class for json read errors
class ReadJsonError(Exception):
    pass

# This function reads the original/generic .json file currently used in MPICH and returns it as a mutable Python object (nested dictionaries)
def read_generic_json_file():
  root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
  json_path = root_path + '/utils/mpich/algorithm_config/generic.json'
  try:
    with open(json_path) as json_file:
      json_file_data = json.load(json_file)
  except FileNotFoundError:
    print(f"Error: The default .json file '{json_path}' was not found.")
    raise ReadJsonError()
  except json.JSONDecodeError:
    print(f"Error: The default .json file '{json_path}' is not a valid JSON file.")
    raise ReadJsonError()
  
  return json_file_data

# This function reads the original/generic .json file currently used in MPICH *for ch4 device tuning* and returns it as a mutable Python object (nested dictionaries)
def read_generic_json_file_ch4():
  root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
  json_path = root_path + '/utils/mpich/algorithm_config/ch4_generic.json'
  try:
    with open(json_path) as json_file:
      json_file_data = json.load(json_file)
  except FileNotFoundError:
    print(f"Error: The default .json file '{json_path}' was not found.")
    raise ReadJsonError()
  except json.JSONDecodeError:
    print(f"Error: The default .json file '{json_path}' is not a valid JSON file.")
    raise ReadJsonError()
  
  return json_file_data

# Reads the "shell" (default selections for edge cases that surround the autotuned selections) from the .json file and returns it as a mutable Python object


def read_collective_shell(collective):
  root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
  json_path = root_path + f"/utils/mpich/algorithm_config/{collective}_shell.json"
  try:
    with open(json_path) as json_file:
      json_file_data = json.load(json_file)
  except FileNotFoundError:
    print(f"Warning: The collective shell file '{json_path}' is not found.")
    raise ReadJsonError()
  except json.JSONDecodeError:
    print(f"Error: The collective shell file '{json_path}' is not a valid JSON file.")
    raise ReadJsonError()
  
  return json_file_data

# Gets the selections for each power of two point
def get_selections(y_test, algs):
  selections = []
  num_algs = len(algs)
  num_sets = int(y_test.size/num_algs)
  for i in range(num_sets):
    selection = np.argmin(y_test[i*num_algs:i*num_algs+num_algs])
    selections.append(selection)

  return selections


# Gets the break points in the space where model prediction switches from one algorithm to another
def get_rules(feature_space, selections, algs, rf):
  # Initialize variables, add initial selection as first rule
  s_prev = selections[0] 
  i = 0
  break_points = {}
  break_points[feature_space[0,:].astype('int').tobytes()] = s_prev

  # Iterate through selection
  for s_cur in selections:

    # If the selection changed, add more rules
    if s_prev != s_cur:
      n_prev = feature_space[i-1,0]
      ppn_prev = feature_space[i-1,1]
      msg_size_prev = feature_space[i-1,2]
      n_cur = feature_space[i,0]
      ppn_cur = feature_space[i,1]
      msg_size_cur = feature_space[i,2]
      
      # If the n and ppn are the same, test the midpoint and make rules
      if (n_prev == n_cur and ppn_prev == ppn_cur):
        msg_size = np.log2((2**(msg_size_cur - 1) + 2 ** (msg_size_cur - 1))/2) + 1
        X_test = add_algs(np.array([n_cur, ppn_cur, msg_size]), algs)
        y_test = rf.predict(X_test)
        fastest_alg = np.argmin(y_test)
        if(fastest_alg == s_prev):
          break_points[feature_space[i,:].astype('int').tobytes()] = s_prev
        elif(fastest_alg == s_cur):
          break_points[feature_space[i-1,:].astype('int').tobytes()] = s_prev
        else:
          break_points[feature_space[i-1,:].astype('int').tobytes()] = s_prev
          break_points[feature_space[i,:].astype('int').tobytes()] = fastest_alg

      # Otherwise, automatically create a rule for both values
      elif(n_prev != n_cur or ppn_prev != ppn_cur):
        break_points[feature_space[i-1,:].astype('int').tobytes()] = s_prev
        break_points[feature_space[i,:].astype('int').tobytes()] = s_cur
      
    s_prev = s_cur
    i+=1

  return break_points


# Converts the highest values to "any"
def any_helper(json_dict):
  if(not json_dict):
    return
  last_key = list(json_dict.keys())[-1]
  if(last_key[:9] == "algorithm"):
    return
  elif last_key[:11] == "composition":
    return
  new_key = last_key[:last_key.find('=') - 1] + "=any"
  json_dict[new_key] = json_dict.pop(last_key)
 
  for nested_dict in json_dict:
    any_helper(json_dict[nested_dict])

# Converts rules into a nested dict
def rules_to_dict(collective, rules, algs):
  n = 0
  ppn = 0
  msg_size = 0
  to_return = OrderedDict()
  cur_comm_size_dict = OrderedDict()
  cur_comm_ppn_dict = OrderedDict()

  mpi_prefix = "MPIR_"
  alg_prefix="algorithm="
  if "_ch4" in collective:
    collective = collective[:-4]
    mpi_prefix = "MPIDI_"
    alg_prefix="composition="

  for feature_set_bytes in rules.keys():
    feature_set = np.frombuffer(feature_set_bytes, dtype=int)
    feature_set = 2 ** (feature_set - 1)
    upstream_change = False
    if(feature_set[0] != n):
      n = feature_set[0]
      cur_comm_size_dict = OrderedDict()
      to_return["comm_size<=" + str(n)] = cur_comm_size_dict
      upstream_change = True
    if(feature_set[1] != ppn or upstream_change):
      ppn = feature_set[1]
      cur_comm_ppn_dict = OrderedDict()
      cur_comm_size_dict["comm_avg_ppn<=" + str(ppn)] = cur_comm_ppn_dict
      upstream_change = True
    if(feature_set[2] != msg_size or upstream_change):
      msg_size = feature_set[2]
      rule_alg_str = algs[rules[feature_set_bytes]]
      alg_str, param_value = split_param_alg(rule_alg_str)
      if collective == "Allgather" or collective == "Reduce_scatter":
        msg_size_str = "total_msg_size"
      else:
        msg_size_str = "avg_msg_size"
      if param_value is None:
        cur_comm_ppn_dict[msg_size_str + "<=" + str(msg_size)] = {alg_prefix + mpi_prefix + collective + "_intra_" + alg_str: {}}
      else:
        param_rule = get_param_rules(collective, alg_str, param_value)
        cur_comm_ppn_dict[msg_size_str + "<=" + str(msg_size)] = {alg_prefix + mpi_prefix + collective + "_intra_" + alg_str: param_rule}

  any_helper(to_return)
  return to_return

# Wraps the autotuner's selections in the shell if necessary
def shell_wrapper(collective, autotuner_json_file_data):
  try:
    shell = read_collective_shell(collective)
  except ReadJsonError: # A collective shell does not exist for this collective, return the selections
    return autotuner_json_file_data
  
  # Perform an iterative DFS to find "replace me" and replace it

  # Initialize a stack with the shell dictionary
  stack = [shell]

  while stack:
      # Pop the last dictionary from the stack
      current_dict = stack.pop()

      # Iterate over a list of keys to avoid modifying the dictionary during iteration
      for key in list(current_dict.keys()):
          value = current_dict[key]

          if key == "replace me":
              # Remove the key and add new key-value pairs from autotuner_json_file_data
              del current_dict[key]
              current_dict.update(autotuner_json_file_data)

          elif isinstance(value, dict):
              # If the value is a dictionary, add it to the stack for further exploration
              stack.append(value)

  return shell


# Replaces the collective in the .json file data with the autotuner's selections
def update_collective(json_file_data, collective, feature_space, rf, algs=None):

  if algs is None:
    algs = read_algs(collective)

  # Unnormalize data
  y_test = rf.predict(add_algs(feature_space, algs))
  selections = get_selections(y_test, algs)

  # Get rules/break points
  rules = get_rules(feature_space, selections, algs, rf)

  # Integrate into json file
  collective_name = "collective=" + collective
  if collective_name[-4:] == "_ch4":
    collective_name = collective_name[:-4]
  collective_caps = collective.capitalize()
  intra = "comm_type=intra"
  for json_collective in json_file_data:
    if json_collective == collective_name:
      for comm_type in json_file_data[json_collective]:
        if(comm_type == intra):
          json_file_data[json_collective][comm_type] = shell_wrapper(collective, rules_to_dict(collective_caps, rules, algs))

  return json_file_data
