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


def get_param_rule(collective, alg_str, param_value):

  if param_value is None:
    return None
  
  param_str = None
  if alg_str ==  "recexch" or alg_str == "recexch_doubling" or alg_str == "recexch_halving":
    param_str = "k"
  if alg_str ==  "tree":
    param_str = "k"
  if alg_str ==  "recursive_multiplying":
    param_str =  "k"
  if alg_str ==  "k_brucks":
    param_str = "k"

  if param_str is None:
    Warning("Param value specified, but param not known")

  return param_str + "=" + str(param_value)