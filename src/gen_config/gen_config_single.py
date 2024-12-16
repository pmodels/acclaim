#This file generates a config file by autotuning a single collective

import sys
import json

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, update_collective

def main():
  n = int(sys.argv[1])
  ppn = int(sys.argv[2])
  msg_size = int(sys.argv[3])
  collective = str(sys.argv[4])
  save_file = str(sys.argv[5])
  json_file_data = read_generic_json_file()

  feature_space, rf = train_model(n, ppn, msg_size, collective)
  json_file_data = update_collective(json_file_data, collective, feature_space, rf)

  with open(save_file, 'w+') as f:
    json.dump(json_file_data, f, indent=2)

  
if __name__ == '__main__':
  main()
