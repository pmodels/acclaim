# This file tests "convergence.py" using unittest
import unittest

import sys
import pathlib
from src.user_config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
  def test_singleton_instance(self):
    # Retrieve the instance of ConfigManager
    instance1 = ConfigManager.get_instance()
    
    # Attempt to retrieve the instance again
    instance2 = ConfigManager.get_instance()
    
    # Check if both instances are the same
    self.assertIs(instance1, instance2, msg="ConfigManager does not implement the Singleton pattern correctly.")
    
  def test_singleton_raises_on_direct_instantiation(self):
    # Check that directly instantiating ConfigManager raises an exception
    with self.assertRaises(Exception) as context:
        ConfigManager()
    self.assertIn("This class is a singleton!", str(context.exception), msg="ConfigManager does not prevent direct instantiation.")

  def test_default_config(self):
    ConfigManager._instance = None
    config = ConfigManager.get_instance()
    # Check that the default config exists and is not none
    self.assertTrue(config is not None, msg="Make sure to run setup!")
    self.assertTrue(config.get_value('settings', 'acclaim_root') is not None, msg="Make sure to run setup!")

  def test_custom_config(self):
    ConfigManager._instance = None
    config = ConfigManager.get_instance(pathlib.Path(__file__).parent / "test_configs", 'test_config.ini')

    # Verify each custom configuration setting
    self.assertEqual(config.get_value('settings', 'root_path'), '/path/to/custom/root')
    self.assertEqual(config.get_value('settings', 'log_level'), 'DEBUG')
    self.assertEqual(config.get_value('database', 'db_host'), 'localhost')
    self.assertEqual(config.get_value('database', 'db_user'), 'admin')
    self.assertEqual(config.get_value('database', 'db_pass'), 'securepass')


if __name__ == '__main__':
  unittest.main()
