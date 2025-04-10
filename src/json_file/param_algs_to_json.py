# This file includes helper methods for dealing with parameterized algorithms
# when convert to .json


#Splits param alg name into alg and param value
def split_param_alg(alg_str):
  # Start from the end of the string and work backwards
  index = len(alg_str)
  
  # Iterate backwards to find where the number starts
  while index > 0 and alg_str[index - 1].isdigit():
      index -= 1
  
  # If index is at the end, there's no number
  if index == len(alg_str):
      return (alg_str, None)
  
  # Split the string into the non-numeric and numeric parts
  non_numeric_part = alg_str[:index]
  numeric_part = int(alg_str[index:])
  
  return (non_numeric_part, numeric_part)


def get_param_rules(collective, alg_str, param_value):

  if param_value is None:
    return None
  
  param_str = None
  if alg_str ==  "recexch" or alg_str == "recexch_doubling" or alg_str == "recexch_halving" or alg_str == "k_reduce_scatter_allgather":
    k_str = "k=" + str(param_value)
    single_phase_str = "single_phase_recv=0"
    return {k_str: {}, single_phase_str: {}}
  if alg_str ==  "tree":
    k_str = "k=" + str(param_value)
    buffer_str = "buffer_per_child=0"
    chunk_size_str = "chunk_size=0"
    tree_type_str= "tree_type=knomial_1"
    return {buffer_str: {}, chunk_size_str: {}, k_str: {}, tree_type_str: {}}
  if alg_str ==  "recursive_multiplying":
    k_str = "k=" + str(param_value)
    return {k_str: {}}
  if alg_str ==  "k_brucks":
    k_str = "k=" + str(param_value)
    return {k_str: {}}

  if param_str is None:
    Warning("Param value specified, but param not known")

  return param_str + "=" + str(param_value)