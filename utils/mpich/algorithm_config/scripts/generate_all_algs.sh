#!/bin/bash
python scripts/genericReader.py | sed 's/  */,/g' > all_algs.csv
sed -i 's/.$//' all_algs.csv
