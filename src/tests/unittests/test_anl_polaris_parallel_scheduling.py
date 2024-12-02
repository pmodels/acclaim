# This file tests "anl_polaris_parallel_scheduling.py" using unittest
import unittest

import os
import sys
import json
import numpy as np

from src.parallel_scheduling.anl_polaris.anl_polaris_parallel_scheduling import (
    Topology, 
    get_rack_name, 
    get_dragonfly_group, 
    get_topology,
    create_nodefile,
)

class TestParallelScheduling(unittest.TestCase):
  def test_get_rack_name(self):
    line = "x3005c0s25b1n0.hsn.cm.polaris.alcf.anl.gov"
    result = get_rack_name(line)
    correct = "3005"
    self.assertEqual(result,correct)
  
  def test_get_dragonfly_group(self):
    line = "x3005c0s25b1n0.hsn.cm.polaris.alcf.anl.gov"
    result = get_dragonfly_group(line)
    correct = 751
    self.assertEqual(result,correct)
  
  def test_create_nodefile(self):
    pwd = os.getcwd()
    nodefile_path = pwd + '/src/tests/unittests/polaris_topos/nodefile.output'
    nodes = ["test1", "test2", "test34"]
    create_nodefile(nodes, nodefile_path)
    with open(nodefile_path, 'r') as f:
      file_lines = f.readlines()
      for i, line in enumerate(file_lines):
        if i < len(nodes) - 1:
          self.assertEqual(line, nodes[i] + "\n")
        else:
          self.assertEqual(line, nodes[i])

    os.remove(nodefile_path)

  def test_get_topology_simple(self):
    pwd = os.getcwd()
    simple_topo_path = pwd + '/src/tests/unittests/polaris_topos/anl_polaris_topo_simple.output'
    topo = get_topology(simple_topo_path)
    self.assertEqual(1, len(topo.dragonfly_groups))
    self.assertEqual(751, topo.dragonfly_groups[0].group_name)
    self.assertEqual(1, len(topo.dragonfly_groups[0].racks))
    self.assertEqual("3005", topo.dragonfly_groups[0].racks[0].name)
    self.assertEqual(2, len(topo.dragonfly_groups[0].racks[0].nodes))
    self.assertEqual(2, topo.dragonfly_groups[0].racks[0].num_nodes())
    self.assertEqual("x3005c0s25b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[0].nodes[0])
    self.assertEqual("x3005c0s31b0n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[0].nodes[1])
  
  def test_get_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/polaris_topos/anl_polaris_topo_complex.output'
    topo = get_topology(example_topo_path)
    self.assertEqual(2, len(topo.dragonfly_groups))
    self.assertEqual(800, topo.dragonfly_groups[0].group_name)
    self.assertEqual(750, topo.dragonfly_groups[1].group_name)
    self.assertEqual(2, len(topo.dragonfly_groups[0].racks))
    self.assertEqual("3201", topo.dragonfly_groups[0].racks[0].name)
    self.assertEqual("3202", topo.dragonfly_groups[0].racks[1].name)
    self.assertEqual(5, len(topo.dragonfly_groups[0].racks[0].nodes))
    self.assertEqual(5, topo.dragonfly_groups[0].racks[0].num_nodes())
    self.assertEqual("x3201c0s31b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[0].nodes[0])
    self.assertEqual("x3201c0s7b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[0].nodes[4])
    self.assertEqual(3, topo.dragonfly_groups[0].racks[1].num_nodes())
    self.assertEqual("x3202c0s13b0n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[1].nodes[0])
    self.assertEqual("x3202c0s19b0n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[0].racks[1].nodes[2])
    self.assertEqual(11, topo.dragonfly_groups[1].racks[0].num_nodes())
    self.assertEqual("x3002c0s19b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[1].racks[0].nodes[0])
    self.assertEqual("x3002c0s7b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[1].racks[0].nodes[10])
    self.assertEqual(5, topo.dragonfly_groups[1].racks[1].num_nodes())
    self.assertEqual("x3003c0s13b0n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[1].racks[1].nodes[0])
    self.assertEqual("x3003c0s1b1n0.hsn.cm.polaris.alcf.anl.gov", topo.dragonfly_groups[1].racks[1].nodes[4])

  def test_fit_topology_simple(self):
    pwd = os.getcwd()
    simple_topo_path = pwd + '/src/tests/unittests/polaris_topos/anl_polaris_topo_simple.output'
    topo = get_topology(simple_topo_path)
    
    first = topo.fit_point(1)
    self.assertEqual(1, len(first))
    self.assertEqual("x3005c0s25b1n0.hsn.cm.polaris.alcf.anl.gov", first[0])
    
    second = topo.fit_point(1)
    self.assertEqual(False, second)
    
    third = topo.fit_point(1)
    self.assertEqual(False, third)
    
    topo.reset_fit()
    fourth = topo.fit_point(2)
    self.assertEqual(2, len(fourth))
    self.assertEqual("x3005c0s25b1n0.hsn.cm.polaris.alcf.anl.gov", fourth[0])
    self.assertEqual("x3005c0s31b0n0.hsn.cm.polaris.alcf.anl.gov", fourth[1])

    fifth = topo.fit_point(1)
    self.assertEqual(False, fifth)
  
  def test_fit_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/polaris_topos/anl_polaris_topo_complex.output'
    topo = get_topology(example_topo_path)

    first = topo.fit_point(7)
    self.assertEqual(7, len(first))
    self.assertEqual("x3201c0s31b1n0.hsn.cm.polaris.alcf.anl.gov", first[0])
    self.assertEqual("x3202c0s13b1n0.hsn.cm.polaris.alcf.anl.gov", first[6])

    second = topo.fit_point(3)
    self.assertEqual(3, len(second))
    self.assertEqual("x3002c0s19b1n0.hsn.cm.polaris.alcf.anl.gov", second[0])
    self.assertEqual("x3002c0s1b1n0.hsn.cm.polaris.alcf.anl.gov", second[2])

    third = topo.fit_point(2)
    self.assertEqual(2, len(third))
    self.assertEqual("x3003c0s13b0n0.hsn.cm.polaris.alcf.anl.gov", third[0])
    self.assertEqual("x3003c0s13b1n0.hsn.cm.polaris.alcf.anl.gov", third[1])

    fourth = topo.fit_point(1)
    self.assertEqual(False, fourth)

    topo.reset_fit()
    fifth = topo.fit_point(1)
    self.assertEqual(1, len(fifth))
    self.assertEqual("x3201c0s31b1n0.hsn.cm.polaris.alcf.anl.gov", fifth[0])

    sixth = topo.fit_point(1)
    self.assertEqual(1, len(sixth))
    self.assertEqual("x3202c0s13b0n0.hsn.cm.polaris.alcf.anl.gov", sixth[0])

    seventh = topo.fit_point(12)
    self.assertEqual(12, len(seventh))
    self.assertEqual("x3002c0s19b1n0.hsn.cm.polaris.alcf.anl.gov", seventh[0])
    self.assertEqual("x3003c0s13b0n0.hsn.cm.polaris.alcf.anl.gov", seventh[11])

    eighth = topo.fit_point(1)
    self.assertEqual(False, eighth)

    topo.reset_fit()
    ninth = topo.fit_point(1000)
    self.assertEqual(False, ninth)

    tenth = topo.fit_point(1)
    self.assertEqual(False, tenth)

    topo.reset_fit()
    eleventh = topo.fit_point(24)
    self.assertEqual(24, len(eleventh))
    self.assertEqual("x3201c0s31b1n0.hsn.cm.polaris.alcf.anl.gov", eleventh[0])
    self.assertEqual("x3003c0s1b1n0.hsn.cm.polaris.alcf.anl.gov", eleventh[23])

    topo.reset_fit()
    twelvth = topo.fit_point(25)
    self.assertEqual(False, twelvth)
 
if __name__ == '__main__':
  unittest.main()
