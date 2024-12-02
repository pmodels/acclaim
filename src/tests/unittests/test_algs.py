# This file tests "algs.py" using unittest
import unittest

import sys
import numpy as np
from src.active_learner.algs import read_algs, add_algs, get_all_algs

class TestAlgs(unittest.TestCase):
  def test_read_algs(self):
    result = read_algs('scatter')
    correct_keys = [0]
    correct_values = ['binomial']
    self.assertEqual(list(result.keys()), correct_keys)
    self.assertEqual(list(result.values()), correct_values)
    result = read_algs('bcast')
    correct_keys = [0,1,2]
    correct_values = ['scatter_recursive_doubling_allgather', 'binomial', 'scatter_ring_allgather']
    self.assertEqual(list(result.keys()), correct_keys)
    self.assertEqual(list(result.values()), correct_values)
  
  def test_get_all_algs(self):
    x = np.array([1,1,1,1])
    keys = [0,1,2]
    algs = ['scatter_recursive_doubling_allgather', 'binomial', 'scatter_ring_allgather']
    algs_dict = dict(zip(keys, algs))
    result = get_all_algs(x, algs_dict)
    correct = np.array([[1,1,1,0],
                        [1,1,1,1],
                        [1,1,1,2]])
    self.assertEqual(result.tolist(), correct.tolist())

  def test_add_algs_1D(self):
    feature_space = np.array([1,1,1])
    algs = read_algs('bcast')
    result = add_algs(feature_space, algs)
    correct = np.array([[1,1,1,0],
                        [1,1,1,1],
                        [1,1,1,2]])
    self.assertEqual(result.tolist(), correct.tolist())
    

  def test_add_algs_2D(self):
    feature_space = np.array([[1,1,1],
                              [1,1,2],
                              [1,2,1],
                              [1,2,2],
                              [2,1,1],
                              [2,1,2],
                              [2,2,1],
                              [2,2,2]])
    algs = read_algs('bcast')
    result = add_algs(feature_space, algs)
    correct = np.array([[1,1,1,0],
                        [1,1,1,1],
                        [1,1,1,2],
                        [1,1,2,0],
                        [1,1,2,1],
                        [1,1,2,2],
                        [1,2,1,0],
                        [1,2,1,1],
                        [1,2,1,2],
                        [1,2,2,0],
                        [1,2,2,1],
                        [1,2,2,2],
                        [2,1,1,0],
                        [2,1,1,1],
                        [2,1,1,2],
                        [2,1,2,0],
                        [2,1,2,1],
                        [2,1,2,2],
                        [2,2,1,0],
                        [2,2,1,1],
                        [2,2,1,2],
                        [2,2,2,0],
                        [2,2,2,1],
                        [2,2,2,2]])
    self.assertEqual(result.tolist(), correct.tolist())


if __name__ == '__main__':
  unittest.main()
