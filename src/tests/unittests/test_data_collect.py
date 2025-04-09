# This file tests "data_collect.py" using unittest
import unittest

import sys
import os
import numpy as np
import subprocess
from src.active_learner.data_collect import collect_point_runner, collect_point_single, collect_point_batch
from src.user_config.config_manager import ConfigManager

class TestDataCollect(unittest.TestCase):
  def test_collect_point_runner(self):
    result = collect_point_runner("bcast", "binomial", 1, 2, 1)
    self.assertGreater(result, 0)
    self.assertLess(result, 10)

  def test_collect_point_param_allreduce_tree(self):
    result = collect_point_runner("allreduce", "tree2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allreduce", "tree4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
  
  def test_collect_point_param_allreduce_recexch(self):
    result = collect_point_runner("allreduce", "recexch2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allreduce", "recexch4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)

  def test_collect_point_param_allreduce_recursive_multiplying(self):
    result = collect_point_runner("allreduce", "recursive_multiplying2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allreduce", "recursive_multiplying4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)

  def test_collect_point_param_allgather_recexch_doubling(self):
    result = collect_point_runner("allgather", "recexch_doubling2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allgather", "recexch_doubling4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)

  def test_collect_point_param_allgather_recexch_halving(self):
    result = collect_point_runner("allgather", "recexch_halving2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allgather", "recexch_halving4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
  
  def test_collect_point_param_allgather_k_brucks(self):
    result = collect_point_runner("allgather", "k_brucks2", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allgather", "k_brucks4", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)

  def test_collect_point_single(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    point = [1, 2, 1, 1]
    result = collect_point_single("bcast", bcast_algs, point)
    self.assertGreater(result, 0)
    self.assertLess(result, 10)

  def test_collect_point_batch(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    points = np.array([[1, 2, 1, 0],
                       [1, 2, 1, 1],
                       [1, 2, 1, 2]])
    n=1
    num_processes=n*ConfigManager.get_instance().get_value('settings', 'max_ppn')
    dummy_topo_instance = ConfigManager.get_instance().get_topology()
    topo_file = dummy_topo_instance.gen_topology_file(num_processes)
    topo = dummy_topo_instance.get_topology(topo_file)

    result = collect_point_batch("bcast", bcast_algs, points, topo)
    self.assertEqual(result.size, 3)
    self.assertGreater(result[0], 0)
    self.assertLess(result[0], 20)
    self.assertGreater(result[1], 0)
    self.assertLess(result[1], 20)
    self.assertGreater(result[2], 0)
    self.assertLess(result[2], 20)

if __name__ == '__main__':
  unittest.main()
