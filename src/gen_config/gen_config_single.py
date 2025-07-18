#This file generates a config file by autotuning a single collective

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
  save_file = str(sys.argv[5])
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

  json_file_data = read_generic_json_file()
  feature_space, rf = train_model(n, ppn, msg_size, collective)
  json_file_data = update_collective(json_file_data, collective, ppn, feature_space, rf)

  with open(save_file, 'w+') as f:
    json.dump(json_file_data, f, indent=2)

  
if __name__ == '__main__':
  main()
