# This file includes methods to generate a custom .json file to configure MPICH

import os
import json
import numpy as np
from src.active_learner.algs import read_algs, add_algs
from collections import OrderedDict

#This function reads the original/generic .json file currently used in MPICH and returns it as a mutable Python object (nested dictionaries)
def read_generic_json_file():
  root_path = os.environ.get('ACCLAIM_ROOT')
  json_path = root_path + '/utils/mpich/algorithm_config/generic.json'
  with open(json_path) as json_file:
    json_file_data = json.load(json_file)
  
  return json_file_data


#Gets the selections for each power of two point
def get_selections(y_test, algs):
  selections = []
  num_algs = len(algs)
  num_sets = int(y_test.size/num_algs)
  for i in range(num_sets):
    selection = np.argmin(y_test[i*num_algs:i*num_algs+num_algs])
    selections.append(selection)

  return selections


#Gets the break points in the space where model prediction switches from one algorithm to another
def get_rules(feature_space, selections, algs, rf):
  #Initialize variables, add initial selection as first rule
  s_prev = selections[0] 
  i = 0
  break_points = {}
  break_points[feature_space[0,:].astype('int').tobytes()] = s_prev

  #Iterate through selection
  for s_cur in selections:

    #If the selection changed, add more rules
    if s_prev != s_cur:
      n_prev = feature_space[i-1,0]
      ppn_prev = feature_space[i-1,1]
      msg_size_prev = feature_space[i-1,2]
      n_cur = feature_space[i,0]
      ppn_cur = feature_space[i,1]
      msg_size_cur = feature_space[i,2]
      
      #If the n and ppn are the same, test the midpoint and make rules
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

      #Otherwise, automatically create a rule for both values
      elif(n_prev != n_cur or ppn_prev != ppn_cur):
        break_points[feature_space[i-1,:].astype('int').tobytes()] = s_prev
        break_points[feature_space[i,:].astype('int').tobytes()] = s_cur
      
    s_prev = s_cur
    i+=1

  return break_points

#Converts the highest values to "any"
def any_helper(json_dict):
  if(not json_dict):
    return
  last_key = list(json_dict.keys())[-1]
  if(last_key[:9] == "algorithm"):
    return
  new_key = last_key[:last_key.find('=') - 1] + "=any"
  json_dict[new_key] = json_dict.pop(last_key)
 
  for nested_dict in json_dict:
    any_helper(json_dict[nested_dict])


#Converts rules into a nested dict
def rules_to_dict(collective, rules, algs):
  n = 0
  ppn = 0
  msg_size = 0
  to_return = OrderedDict()
  cur_comm_size_dict = OrderedDict()
  cur_comm_ppn_dict = OrderedDict()
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
      cur_comm_ppn_dict["avg_msg_size<=" + str(msg_size)] = {"algorithm=MPIR_" + collective + "_intra_" + rule_alg_str: {}} 

  any_helper(to_return)
  return to_return

def update_collective(json_file_data, collective, feature_space, rf):
  algs = read_algs(collective)

  #unnormalize data
  y_test = rf.predict(add_algs(feature_space, algs))
  selections = get_selections(y_test, algs)

  #get rules/break points
  rules = get_rules(feature_space, selections, algs, rf)

  #integrate into json file
  collective_name = "collective=" + collective
  collective_caps = collective.capitalize()
  intra = "comm_type=intra"
  for collective in json_file_data:
    if collective == collective_name:
      for comm_type in json_file_data[collective]:
        if(comm_type == intra):
          json_file_data[collective][comm_type] = rules_to_dict(collective_caps, rules, algs)

  return json_file_data
