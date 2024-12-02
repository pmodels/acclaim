# This file includes utilize functions such as preprocessing, etc.
#

import numpy as np

def preprocess_features(n, ppn, msg_size, type="log"):
  if(type=="log"):
    new_n = np.log2(n) + 1
    new_ppn = np.log2(ppn) + 1
    new_msg_size = np.log2(msg_size) + 1
    return new_n.astype(int), new_ppn.astype(int), new_msg_size.astype(int)

  return n, ppn, msg_size

def unprocess_features(n, ppn, msg_size, type="log"):
  if(type=="log"):
    orig_n = 2 ** (n - 1)
    orig_ppn = 2 ** (ppn - 1)
    orig_msg_size = 2 ** (msg_size - 1)
    return orig_n, orig_ppn, orig_msg_size

  return n, ppn, msg_size

