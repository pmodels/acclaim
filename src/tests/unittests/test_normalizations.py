# This file tests "normalizations.py" using unittest
import unittest

import sys
import numpy as np
from src.active_learner.normalizations import undo_preprocess_input, normalize_output, undo_normalize_output 

class TestNormalizations(unittest.TestCase):
  def test_undo_preprocess_input_simple(self):
    X = np.array([[1,1,1,0],
                  [2,2,2,1],
                  [10,5,3,2],
                  [11,20,21,2]])
    result = undo_preprocess_input(X)
    correct = np.array([[1,1,1,0],
                        [2,2,2,1],
                        [512,16,4,2],
                        [1024,524288,1048576,2]])
    self.assertEqual(result.tolist(), correct.tolist())

  def test_normalize_output_simple(self):
    y = [10,11,12]
    y = np.asarray(y)
    result, original = normalize_output(y, 3, norm_type="alg")
    correct = [1,1.1,1.2]
    correct = np.log10(correct) + 1
    self.assertEqual(result.tolist(), correct.tolist())
    self.assertEqual(original.tolist(), y.tolist())

  def test_normalize_output_harder(self):
    y = [10,11,12,1,2,3,10,11,12]
    y = np.asarray(y)
    result, original = normalize_output(y, 3, norm_type="alg")
    correct = [1,1.1,1.2,1,2,3,1,1.1,1.2]
    correct = np.log10(correct) + 1
    self.assertEqual(result.tolist(), correct.tolist())
    self.assertEqual(original.tolist(), y.tolist())

  def test_undo_normalize_output_simple(self):
    X = np.array([[1,1,1,0],
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
    y_nf = [10,11,12,1,2,3,10,11,12,10,11,12,1,2,3,10,11,12,10,11,12,1,2,3]
    X_set = [[1,1,2,0],
             [1,1,2,1],
             [1,1,2,2],
             [1,2,2,0],
             [1,2,2,1],
             [1,2,2,2]]
    y_set_nf = np.array([1,2,3,10,11,12])
    y_set, _ = normalize_output(y_set_nf, 3, norm_type="alg")
    result = undo_normalize_output(X, y_nf, X_set, y_set, 3, norm_type="alg")
    np.testing.assert_almost_equal(result, y_set_nf)
  

if __name__ == '__main__':
  unittest.main()
