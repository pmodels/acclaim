#This file generates a config file for a single collective from precollected data

import sys
import json
import numpy as np

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, update_collective
from src.user_config.config_manager import ConfigManager

def read_data(data_file):
    data = np.loadtxt(data_file, delimiter=',')

    # Split the data into X_train and y_train
    X_train = data[:, :-1]  # All columns except the last
    y_train = data[:, -1]   # The last column
    
    return X_train, y_train

def main():
  n = int(sys.argv[1])
  ppn = int(sys.argv[2])
  msg_size = int(sys.argv[3])
  collective = str(sys.argv[4])
  data_file = str(sys.argv[5])
  save_file = str(sys.argv[6])
  if len(sys.argv) > 7:
    config_path = str(sys.argv[7])
  else:
    config_path = None
  if len(sys.argv) > 8:
    config_name = str(sys.argv[8])

    #Initialize the ConfigManager if a custom path + name are provided
    ConfigManager.get_instance().reinitialize(config_path, config_name)
  else:
      config_name = None

  json_file_data = read_generic_json_file()
  X_train, y_train = read_data(data_file)
  feature_space, rf = train_model(n, ppn, msg_size, collective, X_train_precollect=X_train, y_train_precollect=y_train)
  json_file_data = update_collective(json_file_data, collective, ppn, feature_space, rf)

  with open(save_file, 'w+') as f:
    json.dump(json_file_data, f, indent=2)

  
if __name__ == '__main__':
  main()
