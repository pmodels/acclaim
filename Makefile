TEST_NAME="test_initialization"
N=4
PPN=32
MSG_SIZE=262144
COLLECTIVE="bcast"
SAVE_FILE="$(ROOT)/fact/test_autotuner.json"
PYTHON=python3

unittest:
	$(PYTHON) -m src.tests.unittests.$(TEST_NAME)

unittest_all:
	$(PYTHON) -m unittest src/tests/unittests/test*.py

bcast_test:
	$(PYTHON) -m src.tests.system.bcast $(N) $(PPN) $(MSG_SIZE)

gen_config_single:
	$(PYTHON) -m src.gen_config.gen_config_single $(N) $(PPN) $(MSG_SIZE) $(COLLECTIVE) $(SAVE_FILE)

gen_config_all:
	$(PYTHON) -m src.gen_config.gen_config_all $(N) $(PPN) $(MSG_SIZE) $(SAVE_FILE)
