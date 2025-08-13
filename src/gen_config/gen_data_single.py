#This file generates a collective data for a single collective

import sys
import json

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, update_collective
from src.user_config.config_manager import ConfigManager

def main():
  n = int(sys.argv[1])
  ppn = int(sys.argv[2])
  msg_size = int(sys.argv[3])
  collective = str(sys.argv[4])
  data_file = str(sys.argv[5])
  if len(sys.argv) > 6:
    config_path = str(sys.argv[6])
  else:
    config_path = None
  if len(sys.argv) > 7:
    config_name = str(sys.argv[7])

    #Initialize the ConfigManager if a custom path + name are provided
    ConfigManager.get_instance().reinitialize(config_path, config_name)
  else:
      config_name = None

  train_model(n, ppn, msg_size, collective, dump_data=True, data_file=data_file)

  
if __name__ == '__main__':
  main()
