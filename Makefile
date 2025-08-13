TEST_NAME="test_initialization"
N=1
PPN=8
MSG_SIZE=262144
COLLECTIVE="allreduce"
COLLECTIVE_LIST="allgather,allreduce,alltoall,bcast,reduce,reduce_scatter"
ACCLAIM_ROOT := $(shell sed -n 's/acclaim_root = *\(.*\) */\1/p' config.ini)
SAVE_FILE="$(ACCLAIM_ROOT)/test_autotuner.json"
DATA_FILE="$(ACCLAIM_ROOT)/data.txt"
PYTHON=python3

unittest:
	$(PYTHON) -m src.tests.unittests.$(TEST_NAME)

unittest_all:
	$(PYTHON) -m unittest src/tests/unittests/test*.py

system_test:
	$(PYTHON) -m src.tests.system.single_collective $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE)

gen_config_single:
	$(PYTHON) -m src.gen_config.gen_config_single $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE) $(SAVE_FILE)

gen_data_single:
	$(PYTHON) -m src.gen_config.gen_data_single $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE) $(DATA_FILE)

gen_config_single_ch4:
	$(PYTHON) -m src.gen_config.gen_config_single_ch4 $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE) $(SAVE_FILE)

gen_config_multiple:
	$(PYTHON) -m src.gen_config.gen_config_multiple $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE_LIST) $(SAVE_FILE)

gen_config_all:
	$(PYTHON) -m src.gen_config.gen_config_all $(N) $(PPN) $(MSG_SIZE) $(SAVE_FILE)
