# This file tests "json.py" using unittest
import unittest

import os
import numpy as np
from pprint import pprint

from sklearn.ensemble import RandomForestRegressor

from src.json_file.json_file import (
    ReadJsonError,
    read_generic_json_file,
    read_generic_json_file_ch4,
    read_collective_shell,
    get_selections,
    get_rules,
    rules_to_dict,
    shell_wrapper,
    any_helper,
    sort_nested_dict,
    update_collective
)
from src.json_file.param_algs_to_json import split_param_alg, get_param_rules
from src.active_learner.algs import read_algs, add_algs
from src.active_learner.normalizations import undo_preprocess_input
from src.user_config.config_manager import ConfigManager

class TestJson(unittest.TestCase):

  def test_read_generic_json_file(self):
    result = read_generic_json_file()
    first_entry_name = next(iter(result.keys()))
    expected_first_entry_name = "collective=bcast"
    self.assertEqual(first_entry_name, expected_first_entry_name)

  def test_read_generic_json_file_ch4(self):
    result = read_generic_json_file_ch4()
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
      "is_op_built_in=no":
      {
          "algorithm=MPIR_Allreduce_intra_recursive_doubling":{}
      },
      "is_op_built_in=yes":
      {
          "is_commutative=no":
          {
              "avg_msg_size<=8":
              {
                  "algorithm=MPIR_Allreduce_intra_recursive_doubling":{}
              },
              "avg_msg_size=any":
              {
                  "count<pow2":
                  {
                      "algorithm=MPIR_Allreduce_intra_recursive_doubling":{}
                  },
                  "count=any":
                  {
                      "algorithm=MPIR_Allreduce_intra_reduce_scatter_allgather":{}
                  }
              }
          },
              "is_commutative=yes":
          {
              "replace me":{},
              "comm_size=any": {
                  "comm_avg_ppn=any": {
                      "avg_msg_size=any":
                      {
                          "count<pow2":
                          {
                              "algorithm=MPIR_Allreduce_intra_recursive_doubling":{}
                          },
                          "count=any":
                          {
                              "algorithm=MPIR_Allreduce_intra_reduce_scatter_allgather":{}
                          }
                      }
                  }
              }        
          }
      }
    }

    self.assertEqual(result, expected_output)

  def test_read_collective_shell_ch4(self):
    collective = "non_existent_collective"
    with self.assertRaises(ReadJsonError):
        read_collective_shell(collective)
    collective="allreduce_ch4"
    result = read_collective_shell(collective)
    expected_output = {
        "comm_hierarchy=parent":
        {
            "is_commutative=yes":
            {
                "comm_size=node_comm_size":
                {
                    "composition=MPIDI_Allreduce_intra_composition_gamma":{}
                },
                "replace me":{}
            },
            "is_commutative=no":
            {
                "comm_size=node_comm_size":
                {
                    "composition=MPIDI_Allreduce_intra_composition_gamma":{}
                },
                "comm_size=any":
                {
                    "composition=MPIDI_Allreduce_intra_composition_beta":{}
                }
            }
        },
        "comm_hierarchy=any":
        {
            "comm_size=node_comm_size":
            {
                "composition=MPIDI_Allreduce_intra_composition_gamma":{}
            },
            "comm_size=any":
            {
                "composition=MPIDI_Allreduce_intra_composition_beta":{}
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

  def test_get_param_rules(self):
    collective = "allreduce"
    alg_str = "recursive_multiplying"
    param_value = 2
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}})
    alg_str = "tree"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}, "buffer_per_child=0": {}, "chunk_size=0": {}, "tree_type=knomial_1": {}})
    alg_str = "recexch"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}, "single_phase_recv=0": {}})
    alg_str = "k_reduce_scatter_allgather"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}, "single_phase_recv=0": {}})
    alg_str = "recexch_doubling"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}, "single_phase_recv=0": {}})
    alg_str = "recexch_halving"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}, "single_phase_recv=0": {}})
    alg_str = "k_brucks"
    result = get_param_rules(collective, alg_str, param_value)
    self.assertEqual(result, {"k=2": {}})
    param_value = None
    result = get_param_rules(collective, alg_str, param_value)
    self.assertIsNone(result)
  
  def test_rules_to_dict_param(self):
    collective="allreduce"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                              [1,2,4],
                              [1,2,5],
                            ])
    rules = {}
    #rules[feature_space[0,:].astype('int').tobytes()] = 3
    rules[np.array([1,2,1]).astype('int').tobytes()] = 0
    rules[np.array([1,2,2]).astype('int').tobytes()] = 1
    rules[np.array([1,2,3]).astype('int').tobytes()] = 0
    rules[np.array([1,2,4]).astype('int').tobytes()] = 3
    rules[np.array([1,2,5]).astype('int').tobytes()] = 0


    rules_dict = rules_to_dict(collective, rules, algs, 2)

    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=2"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_reduce_scatter_allgather")
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=8"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=8"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "buffer_per_child=0")
    self.assertEqual(result[1], "chunk_size=0")
    self.assertEqual(result[2], "k=3")
    self.assertEqual(result[3], "tree_type=knomial_1")

  def test_rules_to_dict_param_ch4(self):
    collective = "allreduce_ch4"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                            ])
    rules = {}
    rules[feature_space[0,:].astype('int').tobytes()] = 0

    rules_dict = rules_to_dict(collective, rules, algs, 2)
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    self.assertEqual(result[0], "composition=MPIDI_allreduce_intra_composition_alpha")

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

    rules_dict = shell_wrapper("no_wrapper", rules_to_dict(collective, rules, algs, 2))
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "buffer_per_child=0")
    self.assertEqual(result[1], "chunk_size=0")
    self.assertEqual(result[2], "k=3")
    self.assertEqual(result[3], "tree_type=knomial_1")

    rules_dict = shell_wrapper(collective, rules_to_dict(collective, rules, algs, 2))
    result = list(rules_dict["is_op_built_in=yes"]["is_commutative=yes"]["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["is_op_built_in=yes"]["is_commutative=yes"]["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "buffer_per_child=0")
    self.assertEqual(result[1], "chunk_size=0")
    self.assertEqual(result[2], "k=3")
    self.assertEqual(result[3], "tree_type=knomial_1")

  def test_shell_wrapper_ch4(self):
    collective="allreduce_ch4"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                            ])
    rules = {}
    rules[feature_space[0,:].astype('int').tobytes()] = 0

    rules_dict = shell_wrapper("no_wrapper", rules_to_dict(collective, rules, algs, 2))
    result = list(rules_dict["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    self.assertEqual(result[0], "composition=MPIDI_allreduce_intra_composition_alpha")

    rules_dict = shell_wrapper(collective, rules_to_dict(collective, rules, algs, 2))
    result = list(rules_dict["comm_hierarchy=parent"]["is_commutative=yes"]["comm_size<=2"]["comm_avg_ppn<=2"]["avg_msg_size<=1"].keys())
    self.assertEqual(result[0], "composition=MPIDI_allreduce_intra_composition_alpha")

  def test_any_helper(self):
    collective="allreduce"
    param_algs_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "utils/mpich/algorithm_config/all_algs_param.csv")
    algs = read_algs(collective, param_algs_path)
    feature_space = np.array([[1,2,1],
                              [1,2,2],
                              [1,2,3],
                            ])
    rules = {}
    rules[feature_space[0,:].astype('int').tobytes()] = 3

    rules_dict = rules_to_dict(collective, rules, algs, 2)

    any_helper(rules_dict)

    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"].keys())
    self.assertEqual(result[0], "algorithm=MPIR_allreduce_intra_tree")
    result = list(rules_dict["comm_size=any"]["comm_avg_ppn=any"]["avg_msg_size=any"]["algorithm=MPIR_allreduce_intra_tree"].keys())
    self.assertEqual(result[0], "buffer_per_child=0")
    self.assertEqual(result[1], "chunk_size=0")
    self.assertEqual(result[2], "k=3")
    self.assertEqual(result[3], "tree_type=knomial_1")

  # sort_nested_dict tests
  def test_simple_sort(self):
      input_data = {
          'key1=any': 'value1',
          'key2=node_comm_size': 'value2',
          'key3': 'value3'
      }
      expected_output = {
          'key2=node_comm_size': 'value2',
          'key3': 'value3',
          'key1=any': 'value1'
      }
      self.assertEqual(sort_nested_dict(input_data), expected_output)

  def test_nested_dict_sort(self):
      input_data = {
          'key1=any': {
              'subkey2=node_comm_size': 'subvalue2',
              'subkey1': 'subvalue1'
          },
          'key2=node_comm_size': 'value2',
          'key3': 'value3'
      }
      expected_output = {
          'key2=node_comm_size': 'value2',
          'key3': 'value3',
          'key1=any': {
              'subkey2=node_comm_size': 'subvalue2',
              'subkey1': 'subvalue1'
          }
      }
      self.assertEqual(sort_nested_dict(input_data), expected_output)

  def test_empty_dict(self):
      input_data = {}
      expected_output = {}
      self.assertEqual(sort_nested_dict(input_data), expected_output)

  def test_no_special_keys(self):
      input_data = {
          'key1': 'value1',
          'key2': 'value2',
          'key3': 'value3'
      }
      expected_output = {
          'key1': 'value1',
          'key2': 'value2',
          'key3': 'value3'
      }
      self.assertEqual(sort_nested_dict(input_data), expected_output)


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

    json_file_data = update_collective(json_file_data, collective, 4, feature_space, rf)    
    answer = False

    first_key = next(iter(json_file_data["collective=bcast"]["comm_type=intra"]["comm_size=any"]))
    second_key = next(iter(json_file_data["collective=bcast"]["comm_type=intra"]["comm_size=any"][first_key]))
    to_check = list(json_file_data["collective=bcast"]["comm_type=intra"]["comm_size=any"][first_key][second_key].keys())
    if(to_check[0] == "algorithm=MPIR_Bcast_intra_scatter_ring_allgather" or to_check[0] == "algorithm=MPIR_Bcast_intra_binomial" or to_check[0] == "algorithm=MPIR_Bcast_intra_scatter_recursive_doubling_allgather"):
      answer = True
    self.assertTrue(answer)

  def test_update_collective_ch4(self):
    collective = "allreduce_ch4"
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
    
    json_file_data = read_generic_json_file_ch4()
    json_file_data = update_collective(json_file_data, collective, 4, feature_space, rf)
    answer = False

    first_key = next(iter(json_file_data["collective=allreduce"]["comm_type=intra"]["comm_hierarchy=parent"]["is_commutative=yes"]["comm_size=any"]))
    second_key = next(iter(json_file_data["collective=allreduce"]["comm_type=intra"]["comm_hierarchy=parent"]["is_commutative=yes"]["comm_size=any"][first_key]))
    to_check = list(json_file_data["collective=allreduce"]["comm_type=intra"]["comm_hierarchy=parent"]["is_commutative=yes"]["comm_size=any"][first_key][second_key].keys())
    if(to_check[0] == "composition=MPIDI_Allreduce_intra_composition_alpha" or to_check[0] == "composition=MPIDI_Allreduce_intra_composition_beta" or to_check[0] == "composition=MPIDI_Allreduce_intra_composition_delta"):
      answer = True
    self.assertTrue(answer)

if __name__ == '__main__':
  unittest.main()
