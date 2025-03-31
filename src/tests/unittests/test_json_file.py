# This file tests "json.py" using unittest
import unittest

import os
import numpy as np

from sklearn.ensemble import RandomForestRegressor

from src.json_file.json_file import ReadJsonError, read_generic_json_file, read_collective_shell, get_selections, get_rules, rules_to_dict, shell_wrapper, update_collective
from src.json_file.param_algs_to_json import split_param_alg, get_param_rule
from src.active_learner.algs import read_algs, add_algs
from src.active_learner.normalizations import undo_preprocess_input
from src.user_config.config_manager import ConfigManager

class TestJson(unittest.TestCase):

  def test_read_generic_json_file(self):
    result = read_generic_json_file()
    first_entry_name = next(iter(result.keys()))
    expected_first_entry_name = "collective=bcast"
    self.assertEqual(first_entry_name, expected_first_entry_name)

  def test_read_collective_shell(self):
    collective = "non_existent_collective"
    with self.assertRaises(ReadJsonError):
        read_collective_shell(collective)
    collective="allreduce"
    result = read_collective_shell(collective)
    expected_output = {
              "is_op_built_in=no": {
                  "algorithm=MPIR_Allreduce_intra_recursive_doubling": {}
              },
              "is_op_built_in=yes": {
                  "is_commutative=no": {
                      "avg_msg_size<=8": {
                          "algorithm=MPIR_Allreduce_intra_recursive_doubling": {}
                      },
                      "avg_msg_size=any": {
                          "count<pow2": {
                              "algorithm=MPIR_Allreduce_intra_recursive_doubling": {}
                          },
                          "count=any": {
                              "algorithm=MPIR_Allreduce_intra_reduce_scatter_allgather": {}
                          }
                      }
                  },
                  "is_commutative=yes": {
                      "replace me": {}
                  }
              }
            }

    self.assertEqual(result, expected_output)

  def test_get_selections(self):
    collective="bcast"
    algs = read_algs(collective)
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
  
  def test_split_param_alg(self):
    alg_str = "recursive_doubling"
    result = split_param_alg(alg_str)
    self.assertEqual(result[0], "recursive_doubling")
    self.assertIsNone(result[1])
    alg_str = "recursive_multiplying2"
    result = split_param_alg(alg_str)
    self.assertEqual(result[0], "recursive_multiplying")
    self.assertEqual(result[1], 2)
    alg_str = "recursive_multiplying16"
    result = split_param_alg(alg_str)
    self.assertEqual(result[0], "recursive_multiplying")
    self.assertEqual(result[1], 16)

  def test_get_param_rule(self):
    collective = "allreduce"
    alg_str = "recursive_multiplying"
    param_value = 2
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    alg_str = "tree"
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    alg_str = "recexch"
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    alg_str = "recexch_doubling"
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    alg_str = "recexch_halving"
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    alg_str = "k_brucks"
    result = get_param_rule(collective, alg_str, param_value)
    self.assertEqual(result, "k=2")
    param_value = None
    result = get_param_rule(collective, alg_str, param_value)
    self.assertIsNone(result)
  
  def test_rules_to_dict_param(self):
    collective="allreduce"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                            ])
    rules = {}
    rules[feature_space[0,:].astype('int').tobytes()] = 3

    rules_dict = rules_to_dict(collective, rules, algs)
    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "k=3")

  def test_shell_wrapper(self):
    collective="allreduce"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                            ])
    rules = {}
    rules[feature_space[0,:].astype('int').tobytes()] = 3

    rules_dict = shell_wrapper("no_wrapper", rules_to_dict(collective, rules, algs))
    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "k=3")

    rules_dict = shell_wrapper(collective, rules_to_dict(collective, rules, algs))
    result = list(rules_dict["is_op_built_in=yes"]["is_commutative=yes"]["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["is_op_built_in=yes"]["is_commutative=yes"]["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "k=3")

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
