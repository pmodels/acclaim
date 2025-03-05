# This file tests "initialization.py" using unittest
import unittest

import sys
import numpy as np
from src.active_learner.initialization import create_feature_space, get_initial_points


class TestInitialization(unittest.TestCase):
  def test_simple_feature_space(self):
    result = create_feature_space(2,2,2,"bcast")
    correct = np.array([[1,2,1],
                        [1,2,2],
                        [2,1,1],
                        [2,1,2],
                        [2,2,1],
                        [2,2,2]])
    self.assertEqual(result.tolist(), correct.tolist())
  
  def test_simple_reduce_feature_space(self):
    result = create_feature_space(2,2,3,"reduce_scatter")
    correct = np.array([[1,2,3],
                        [2,1,3],
                        [2,2,3]])
    self.assertEqual(result.tolist(), correct.tolist())

  def test_bigger_feature_space(self):
    result = create_feature_space(2,3,4,"bcast")
    correct = np.array([[1,2,1],
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
    self.assertEqual(result.tolist(), correct.tolist())

  def test_simple_get_initial_points(self):
    X = np.array([[1,1,1],
                  [1,1,2],
                  [1,2,1],
                  [1,2,2],
                  [2,1,1],
                  [2,1,2],
                  [2,2,1],
                  [2,2,2],
                  [2,2,3],
                  [2,2,4]])
    result = get_initial_points(X)
    correct = np.array([[1,1,1],
                        [1,2,1],
                        [2,1,1]])
    self.assertEqual(result.tolist(), correct.tolist())
  def test_bigger_get_initial_points(self):
    X = np.array([[1,1,1],
                  [1,1,2],
                  [1,1,3],
                  [1,1,4],
                  [1,2,1],
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
    result = get_initial_points(X)
    correct = np.array([[1,1,1],
                        [1,2,2],
                        [1,3,4]])
    self.assertEqual(result.tolist(), correct.tolist())
    

if __name__ == '__main__':
  unittest.main()
