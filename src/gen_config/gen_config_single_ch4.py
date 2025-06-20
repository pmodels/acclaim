#This file generates a config file by autotuning a single collective

import sys
import json

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, read_generic_json_file_ch4, update_collective
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

  collective_ch4 = collective + "_ch4"
  json_file_data_ch4 = read_generic_json_file_ch4()
  feature_space_ch4, rf_ch4 = train_model(n, ppn, msg_size, collective_ch4)
  json_file_data_ch4 = update_collective(json_file_data_ch4, collective_ch4, ppn, feature_space_ch4, rf_ch4)

  with open(save_file, 'w+') as f:
    json.dump(json_file_data_ch4, f, indent=2)

  
if __name__ == '__main__':
  main()
