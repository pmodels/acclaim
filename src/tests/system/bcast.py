# This is just a test

import sys
import json

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, update_collective

def main():
  n = int(sys.argv[1])
  ppn = int(sys.argv[2])
  msg_size = int(sys.argv[3])
  collective = "bcast"

  feature_space, rf = train_model(n, ppn, msg_size, collective)

  json_file_data = read_generic_json_file()

  json_file_data = update_collective(json_file_data, collective, feature_space, rf)

  print(json.dumps(json_file_data, indent=2))

if __name__ == "__main__":
  main()
