#This file generates a config file by autotuning all "interesting" collectives
#Interesting = non-variable, blocking collectives that have more than one implementation in MPICH

import sys
import json

from src.active_learner.active_learner import train_model
from src.json_file.json_file import read_generic_json_file, update_collective

def main():
  n = int(sys.argv[1])
  ppn = int(sys.argv[2])
  msg_size = int(sys.argv[3])
  save_file = str(sys.argv[4])
  collectives = ['allgather','allreduce','alltoall','bcast','reduce','reduce_scatter']
  collectives_input = str(sys.argv[5])
  
  # Parse the comma-separated collectives into a list
  collectives = collectives_input.split(',')

  for collective in collectives:
    feature_space, rf = train_model(n, ppn, msg_size, collective)
    json_file_data = update_collective(json_file_data, collective, feature_space, rf)

  with open(save_file, 'w+') as f:
    json.dump(json_file_data, f, indent=2)

  
if __name__ == '__main__':
  main()
