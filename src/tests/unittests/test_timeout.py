# This file tests the timeout in "active_learner.py" using unittest
import unittest

import sys
import pathlib
import io
from contextlib import redirect_stdout
from src.user_config.config_manager import ConfigManager
from src.active_learner.active_learner import train_model

class TestTimeout(unittest.TestCase):
  def test_timeout(self):
    ConfigManager._instance = None
    timeout = ConfigManager.get_instance().get_value('settings', 'timeout')
    ConfigManager.get_instance()._set_value('settings', 'timeout', '0')

    n = 1
    ppn = 8
    msg_size = 262144
    collective = 'scatter'

    with io.StringIO() as buf, redirect_stdout(buf):
      feature_space, rf = train_model(n, ppn, msg_size, collective)
      self.assertIn("Timeout reached, exiting!", buf.getvalue())


if __name__ == '__main__':
  unittest.main()
