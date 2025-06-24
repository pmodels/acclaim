# This file tests "data_collect.py" using unittest
import re
import unittest
from unittest.mock import patch

import sys
import os
import numpy as np
import subprocess
import shutil
from src.active_learner.data_collect import run_mb_runner, parse_runner_output, collect_point_runner, collect_point_single, collect_point_batch, create_unique_directory
from src.user_config.config_manager import ConfigManager

class TestDataCollect(unittest.TestCase):
  def test_create_unique_directory(self):
      # Create a temporary root path for testing
      self.test_root_path = os.path.join(ConfigManager.get_instance().get_value('settings', 'acclaim_root'), "src//tests/unittests/test_dir")
      os.makedirs(self.test_root_path, exist_ok=True)

      # Call the function to create a unique directory
      unique_dir_path = create_unique_directory(self.test_root_path)

      # Check if the directory was created
      self.assertTrue(os.path.exists(unique_dir_path))

      # Check if the directory is indeed unique
      # Create another directory and ensure the paths are different
      another_unique_dir_path = create_unique_directory(self.test_root_path)
      self.assertNotEqual(unique_dir_path, another_unique_dir_path)

      # Check if the directory name contains a timestamp and UUID
      dir_name = os.path.basename(unique_dir_path)
      parts = dir_name.split('_')
      self.assertEqual(len(parts), 2)
      timestamp_parts = parts[0].split('-')
      self.assertTrue(timestamp_parts[0].isdigit()) # Timestamp part 1
      self.assertTrue(timestamp_parts[1].isdigit()) # Timestamp part 2
      self.assertEqual(len(parts[1]), 32)  # UUID part

      # Clean up the temporary root path after tests
      shutil.rmtree(self.test_root_path)
  
  def test_run_mb_runner(self):
      # Call the function with the test parameters
      result_stdout, result_stderr = run_mb_runner("bcast", "binomial", 1, 2, 1)

      # Expected patterns
      expected_header = "Broadcast Latency Test"
      expected_datatype = "# Datatype"
      expected_size_label = "# Size       Avg Latency(us)"
      expected_size_value = "1"

      # Assert that the expected header is present
      self.assertIn(expected_header, result_stdout)

      # Assert that the expected datatype line is present
      self.assertIn(expected_datatype, result_stdout)

      # Assert that the size label line is present
      self.assertIn(expected_size_label, result_stdout)

      # Use a regular expression to check the size and latency format
      latency_pattern = re.compile(rf"{expected_size_value}\s+\d+\.\d+")
      self.assertRegex(result_stdout, latency_pattern)

      # Assert that stderr is empty
      self.assertEqual(result_stderr.strip(), "")
  
  def test_parse_runner_output(self):
      # Input data for the test
      input_data = """\
# OSU MPI-SYCL Broadcast Latency Test v7.5
# Datatype: MPI_CHAR.
# Size       Avg Latency(us)
1                       2.20
"""
      # Expected result
      expected_latency = 2.20

      # Call the parse_runner_output function
      result = parse_runner_output(input_data, None, "bcast", "binomial", 1, 2, 1)

      # Assert that the result matches the expected latency
      self.assertAlmostEqual(result, expected_latency, places=2)

  def test_collect_point_runner(self):
    result = collect_point_runner("bcast", "binomial", 1, 2, 1)
    self.assertGreater(result, 0)
    self.assertLess(result, 20)

  def test_collect_point_runner_fail(self):
    with self.assertRaises(subprocess.CalledProcessError) as cm:
        collect_point_runner("not_a_collective", "binomial", 1, 2, 1)

  def test_run_mb_runner_with_error_but_valid_output(self):
      # Simulate the subprocess output and error
      simulated_stdout = """\
# OSU MPI-SYCL Reduce_scatter Latency Test v7.5
# Datatype: MPI_INT.
# Size       Avg Latency(us)
65536                 821.05
"""
      simulated_stderr = "free(): invalid pointer\nfree(): invalid pointer\n"

      # Mock the subprocess.run method to simulate the error scenario
      with patch('subprocess.run') as mock_run:
          mock_run.side_effect = subprocess.CalledProcessError(
              returncode=1,
              cmd='mocked_command',
              output=simulated_stdout,
              stderr=simulated_stderr
          )

          # Call the function with the test parameters
          result_stdout, result_stderr = run_mb_runner("reduce_scatter", "binomial", 1, 2, 65536)

          # Assert that the expected header is present
          expected_header = "Reduce_scatter Latency Test"
          self.assertIn(expected_header, result_stdout)

          # Assert that the expected datatype line is present
          expected_datatype = "# Datatype: MPI_INT."
          self.assertIn(expected_datatype, result_stdout)

          # Assert that the size label line is present
          expected_size_label = "# Size       Avg Latency(us)"
          self.assertIn(expected_size_label, result_stdout)

          # Use a regular expression to check the size and latency format
          expected_size_value = "65536"
          latency_pattern = re.compile(rf"{expected_size_value}\s+\d+\.\d+")
          self.assertRegex(result_stdout, latency_pattern)

          # Assert that stderr contains the simulated error message
          self.assertIn("free(): invalid pointer", result_stderr)

          # Call the parse_runner_output function to ensure parsing works despite the error
          result = parse_runner_output(result_stdout, result_stderr, "reduce_scatter", "binomial", 1, 2, 65536)

          # Assert that the parsed result is correct
          expected_latency = 821.05
          self.assertAlmostEqual(result, expected_latency, places=2)

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

  def test_collect_point_param_allreduce_ch4_alpha(self):
    result = collect_point_runner("allreduce_ch4", "alpha", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)
    result = collect_point_runner("allreduce_ch4", "alpha", 1, 2, 4)
    self.assertGreater(result, 0)
    self.assertLess(result, 1000)

  def test_collect_point_single(self):
    bcast_algs = {0: 'scatter_recursive_doubling_allgather', 1: 'binomial', 2: 'scatter_ring_allgather'}
    point = [1, 2, 1, 1]
    result = collect_point_single("bcast", bcast_algs, point)
    self.assertGreater(result, 0)
    self.assertLess(result, 10)

  def test_collect_point_single_ch4(self):
    allreduce_algs = {0: 'alpha', 1: 'beta'}
    point = [1, 2, 4, 1]
    result = collect_point_single("allreduce_ch4", allreduce_algs, point)
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
