# This file tests "utils.py" using unittest
import unittest

import sys
import numpy as np
from src.active_learner.utils import preprocess_features, unprocess_features


class TestInitialization(unittest.TestCase):
  def test_preprocess_features(self):
    n, ppn, msg_size = preprocess_features(1,1,1)
    self.assertEqual(1,n)
    self.assertEqual(1,ppn)
    self.assertEqual(1,msg_size)
    n, ppn, msg_size = preprocess_features(2,2,2)
    self.assertEqual(2,n)
    self.assertEqual(2,ppn)
    self.assertEqual(2,msg_size)
    n, ppn, msg_size = preprocess_features(4,8,16)
    self.assertEqual(3,n)
    self.assertEqual(4,ppn)
    self.assertEqual(5,msg_size)
    n, ppn, msg_size = preprocess_features(128,512,1048576)
    self.assertEqual(8,n)
    self.assertEqual(10,ppn)
    self.assertEqual(21,msg_size)

  def test_unprocess_features(self):
    n, ppn, msg_size = unprocess_features(1,1,1)
    self.assertEqual(1,n)
    self.assertEqual(1,ppn)
    self.assertEqual(1,msg_size)
    n, ppn, msg_size = unprocess_features(2,2,2)
    self.assertEqual(2,n)
    self.assertEqual(2,ppn)
    self.assertEqual(2,msg_size)
    n, ppn, msg_size = unprocess_features(3,4,5)
    self.assertEqual(4,n)
    self.assertEqual(8,ppn)
    self.assertEqual(16,msg_size)
    n, ppn, msg_size = unprocess_features(8,10,21)
    self.assertEqual(128,n)
    self.assertEqual(512,ppn)
    self.assertEqual(1048576,msg_size)

if __name__ == '__main__':
  unittest.main()
