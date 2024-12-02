# This file tests "json.py" using unittest
import unittest

import sys
import json
import numpy as np

from sklearn.ensemble import RandomForestRegressor

from src.json_file.json_file import read_generic_json_file, get_selections, get_rules, rules_to_dict, update_collective
from src.active_learner.algs import read_algs, add_algs
from src.active_learner.normalizations import undo_preprocess_input

class TestJson(unittest.TestCase):
  def test_get_selections(self):
    collective="bcast"
    algs = read_algs(collective)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,3,1],
                              [1,3,2],
                              [2,1,1],
                              [2,1,2]])
    y_test = np.array([1,2,3,3,2,1,2,1,3,1,2,3,3,2,1,2,1,3]) #Correct selections are the minimum every 3, so 0,2,1,0,2,1
    result = get_selections(y_test, algs)
    correct = [0,2,1,0,2,1]
    self.assertEqual(result, correct)

  def test_get_rules(self):
    collective="bcast"
    algs = read_algs(collective)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,3,1],
                              [1,3,2],
                              [2,1,1],
                              [2,1,2]])
    X = add_algs(feature_space, algs)
    y = np.array([1,2,3,3,2,1,2,1,3,1,2,3,3,2,1,2,1,3]) 
    selections = get_selections(y, algs)
    rf = RandomForestRegressor()
    rf.fit(X, y)
    result = get_rules(feature_space, selections,algs,rf)
    result_list = []
    for key in result.keys():
      result_list.append(np.frombuffer(key, dtype=int).tolist())
    correct_keys= np.array([[1,2,1],
                            [1,2,2],
                            [1,3,1],
                            [1,3,2],
                            [2,1,1]])
    correct_values = [0,2,1,0,2]
    self.assertEqual(result_list, correct_keys.tolist())
    self.assertEqual(list(result.values()), correct_values)
    #self.assertEqual(result, correct)
    

  def test_update_collective(self):
    collective="bcast"
    algs = read_algs(collective)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                              [1,2,4],
                              [1,3,1],
                              [1,3,2],
                              [1,3,3],
                              [1,3,4],
                              [2,1,1],
                              [2,1,2],
                              [2,1,3],
                              [2,1,4],
                              [2,2,1],
                              [2,2,2],
                              [2,2,3],
                              [2,2,4],
                              [2,3,1],
                              [2,3,2],
                              [2,3,3],
                              [2,3,4]])
    X = add_algs(feature_space, algs)
    X_nf = undo_preprocess_input(X) 
    y = np.random.rand(X_nf.shape[0])
    result = add_algs(feature_space, algs)
    rf = RandomForestRegressor()
    rf.fit(X, y)
    
    json_file_data = read_generic_json_file()

    json_file_data = update_collective(json_file_data, collective, feature_space, rf)    
    answer = False
    to_check = list(json_file_data["collective=bcast"]["comm_type=intra"]["comm_size<=1"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    if(to_check[0] == "algorithm=MPIR_Bcast_intra_scatter_ring_allgather" or to_check[0] == "algorithm=MPIR_Bcast_intra_binomial" or to_check[0] == "algorithm=MPIR_Bcast_intra_scatter_recursive_doubling_allgather"):
      answer = True
    self.assertTrue(answer)

if __name__ == '__main__':
  unittest.main()
