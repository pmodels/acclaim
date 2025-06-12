# This file tests "convergence.py" using unittest
import unittest

import sys
import numpy as np
from src.active_learner.convergence import convergence_criteria

class TestConvergence(unittest.TestCase):
  def test_convergence_criteria_simple(self):
    vals = [1,1,1,1]
    result = convergence_criteria(vals)
    correct = True
    self.assertEqual(result, correct)

    vals = [1,2,3,4]
    result = convergence_criteria(vals)
    correct = False
    self.assertEqual(result, correct)
  
  def test_convergence_criteria_harder(self):
    vals = [1,1.00000000001,1.000000000015,1.00000000002]
    result = convergence_criteria(vals)
    correct = True
    self.assertEqual(result, correct)

    vals = [1,1,1,1.0011]
    result = convergence_criteria(vals)
    correct = False
    self.assertEqual(result, correct)


if __name__ == '__main__':
  unittest.main()
