# This file reads the user input from config.ini in the root directory

import pathlib
import configparser

class ConfigManager:
    _instance = None

    @staticmethod
    def get_instance(config_dir=None, config_name="config.ini"):
        if ConfigManager._instance is None:
            ConfigManager(config_dir, config_name)
        return ConfigManager._instance

    def __init__(self, config_dir=None, config_name="config.ini"):
        if ConfigManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ConfigManager._instance = self
            self.parser = configparser.ConfigParser()
            if config_dir is None:
                config_dir = pathlib.Path(__file__).parent.parent.parent
            config_path = config_dir / config_name
            self.parser.read(config_path)
        

    def get_value(self, section, key):
       if self.parser is None:
           self.get_instance()
       return self.parser[section][key]