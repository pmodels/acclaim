import json
import sys

def gatherAlgorithms( obj ):
  results = gatherAlgorithmsHelper(obj);
  for result in results:
    print(result),
  return

def gatherAlgorithmsHelper( obj ):
  algs = set()
  for sub_obj in obj:
    if(sub_obj[:10] == "algorithm="):
      if(sub_obj.find("inter") == -1):
        algs.add(sub_obj[10:])
    else:
      algs.update(gatherAlgorithmsHelper(obj[sub_obj]))
  return algs

generic_file = open('generic.json')

data = json.loads(generic_file.read())

for collective in data:
  print(collective[11:]),
  gatherAlgorithms(data[collective])
  print("\n")

generic_file.close()

