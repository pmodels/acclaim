# This file tests "data_collect.py" using unittest
import unittest

import sys
import os
import numpy as np
from src.active_learner.data_collect import collect_point, collect_point_single, collect_point_batch
from src.parallel_scheduling.anl_polaris.anl_polaris_parallel_scheduling import Topology, get_topology

class TestDataCollect(unittest.TestCase):
  """
  def test_collect_point(self):
    result = collect_point("bcast", "binomial", 1, 2, 1)
    self.assertGreater(result, 0)
    self.assertLess(result, 10)

  def test_collect_point_single(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    point = np.zeros(4)
    point = [1, 2, 1, 1]
    result = collect_point_single("bcast", bcast_algs, point)
    self.assertGreater(result, 0)
    self.assertLess(result, 10)

  def test_collect_point_batch(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    points = np.array([[1, 2, 1, 0],
                       [1, 2, 1, 1],
                       [1, 2, 1, 2]])
    result = collect_point_batch(2, "bcast", bcast_algs, points)
    self.assertEqual(result.size, 3)
    self.assertGreater(result[0], 0)
    self.assertLess(result[0], 10)
    self.assertGreater(result[1], 0)
    self.assertLess(result[1], 10)
    self.assertGreater(result[2], 0)
    self.assertLess(result[2], 10)
  """
  def test_collect_point_batch_parallel_theta(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    points = np.array([[1, 2, 1, 0],
                       [1, 2, 1, 1],
                       [1, 2, 1, 2],
                       [1, 2, 2, 0],
                       [1, 2, 2, 1],
                       [1, 2, 2, 2]])
    topo_path = os.environ.get('PBS_NODEFILE')
    if not topo_path:
        topo_path = os.getcwd() + "/src/tests/unittests/polaris_topos/anl_polaris_topo_simple.output"
    print("Topo file:")
    with open(topo_path, 'r') as file:
      print(file.read())
    topo=get_topology(topo_path)
    result = collect_point_batch("bcast", bcast_algs, points, parallel=1, topo=topo)
    self.assertEqual(result.size, 6)
    self.assertGreater(result[0], 0)
    self.assertLess(result[0], 10)
    self.assertGreater(result[1], 0)
    self.assertLess(result[1], 10)
    self.assertGreater(result[2], 0)
    self.assertLess(result[2], 10)
    self.assertGreater(result[3], 0)
    self.assertLess(result[3], 10)
    self.assertGreater(result[4], 0)
    self.assertLess(result[4], 10)
    self.assertGreater(result[5], 0)
    self.assertLess(result[5], 10)

if __name__ == '__main__':
  unittest.main()