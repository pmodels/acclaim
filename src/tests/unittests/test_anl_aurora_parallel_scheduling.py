# This file tests "anl_aurora_parallel_scheduling.py" using unittest
import unittest

import os
import sys
import json
import numpy as np

from src.parallel_scheduling.anl_aurora.anl_aurora_parallel_scheduling import (
    Topology,
    _get_node_name,
    _get_chassis_name,
    _get_rack_name, 
    _get_dragonfly_group
)

class TestParallelScheduling(unittest.TestCase):
  def test_get_node_name(self):
    line = "x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov\n"
    result = _get_node_name(line)
    correct = "x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov"
    self.assertEqual(result,correct)

  def test_get_chassis_name(self):
    line = "x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov"
    result = _get_chassis_name(line)
    correct = "3"
    self.assertEqual(result,correct)

  def test_get_rack_name(self):
    line = "x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov"
    result = _get_rack_name(line)
    correct = "4407"
    self.assertEqual(result,correct)
  
  def test_get_dragonfly_group(self):
    line = "x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov"
    result = _get_dragonfly_group(line)
    correct = 4407
    self.assertEqual(result,correct)
  
  def test_create_nodefile(self):
    pwd = os.getcwd()
    nodefile_path = pwd + '/src/tests/unittests/aurora_topos/nodefile.output'
    nodes = ["test1", "test2", "test34"]
    Topology.create_nodefile(nodes, nodefile_path)
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
    simple_topo_path = pwd + '/src/tests/unittests/aurora_topos/anl_aurora_topo_4.output'
    topo = Topology.get_topology(simple_topo_path)
    self.assertEqual(1, len(topo.dragonfly_groups))
    self.assertEqual(4407, topo.dragonfly_groups[0].group_name)
    self.assertEqual(1, len(topo.dragonfly_groups[0].chassis))
    self.assertEqual("3", topo.dragonfly_groups[0].chassis[0].name)
    self.assertEqual(4, len(topo.dragonfly_groups[0].chassis[0].nodes))
    self.assertEqual(4, topo.dragonfly_groups[0].chassis[0].num_nodes())
    self.assertEqual("x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[0].nodes[0])
    self.assertEqual("x4407c3s4b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[0].nodes[1])
  
  def test_get_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/aurora_topos/anl_aurora_topo_32.output'
    topo = Topology.get_topology(example_topo_path)
    self.assertEqual(2, len(topo.dragonfly_groups))
    self.assertEqual(4211, topo.dragonfly_groups[0].group_name)
    self.assertEqual(4213, topo.dragonfly_groups[1].group_name)
    self.assertEqual(7, len(topo.dragonfly_groups[0].chassis))
    self.assertEqual("1", topo.dragonfly_groups[0].chassis[0].name)
    self.assertEqual("2", topo.dragonfly_groups[0].chassis[1].name)
    self.assertEqual(4, len(topo.dragonfly_groups[0].chassis[0].nodes))
    self.assertEqual(4, topo.dragonfly_groups[0].chassis[0].num_nodes())
    self.assertEqual("x4211c1s1b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[0].nodes[0])
    self.assertEqual("x4211c1s7b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[0].nodes[3])
    self.assertEqual(3, topo.dragonfly_groups[0].chassis[6].num_nodes())
    self.assertEqual("x4211c7s2b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[6].nodes[0])
    self.assertEqual("x4211c7s4b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[0].chassis[6].nodes[2])
    self.assertEqual(3, topo.dragonfly_groups[1].chassis[0].num_nodes())
    self.assertEqual("x4213c0s0b0n0.hostmgmt2213.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[1].chassis[0].nodes[0])
    self.assertEqual("x4213c0s7b0n0.hostmgmt2213.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[1].chassis[0].nodes[2])
    self.assertEqual(1, topo.dragonfly_groups[1].chassis[1].num_nodes())
    self.assertEqual("x4213c2s3b0n0.hostmgmt2213.cm.aurora.alcf.anl.gov", topo.dragonfly_groups[1].chassis[1].nodes[0])

  def test_fit_topology_simple(self):
    pwd = os.getcwd()
    simple_topo_path = pwd + '/src/tests/unittests/aurora_topos/anl_aurora_topo_4.output'
    topo = Topology.get_topology(simple_topo_path)
    
    first = topo.fit_point(1)
    self.assertEqual(1, len(first))
    self.assertEqual("x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov", first[0])
    
    second = topo.fit_point(1)
    self.assertEqual(False, second)
    
    third = topo.fit_point(1)
    self.assertEqual(False, third)
    
    topo.reset_fit()
    fourth = topo.fit_point(2)
    self.assertEqual(2, len(fourth))
    self.assertEqual("x4407c3s1b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov", fourth[0])
    self.assertEqual("x4407c3s4b0n0.hostmgmt2407.cm.aurora.alcf.anl.gov", fourth[1])

    fifth = topo.fit_point(1)
    self.assertEqual(False, fifth)
  
  def test_fit_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/aurora_topos/anl_aurora_topo_32.output'
    topo = Topology.get_topology(example_topo_path)

    first = topo.fit_point(7)
    self.assertEqual(7, len(first))
    self.assertEqual("x4211c1s1b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", first[0])
    self.assertEqual("x4211c2s5b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", first[6])

    second = topo.fit_point(3)
    self.assertEqual(3, len(second))
    self.assertEqual("x4211c3s0b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", second[0])
    self.assertEqual("x4211c3s3b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", second[2])

    third = topo.fit_point(2)
    self.assertEqual(2, len(third))
    self.assertEqual("x4211c4s0b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", third[0])
    self.assertEqual("x4211c4s2b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", third[1])

    fourth = topo.fit_point(16)
    self.assertEqual(False, fourth)

    topo.reset_fit()
    fifth = topo.fit_point(1)
    self.assertEqual(1, len(fifth))
    self.assertEqual("x4211c1s1b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", fifth[0])

    sixth = topo.fit_point(1)
    self.assertEqual(1, len(sixth))
    self.assertEqual("x4211c2s0b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", sixth[0])

    seventh = topo.fit_point(12)
    self.assertEqual(12, len(seventh))
    self.assertEqual("x4211c3s0b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", seventh[0])
    self.assertEqual("x4211c5s4b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", seventh[11])

    eighth = topo.fit_point(13)
    self.assertEqual(False, eighth)

    topo.reset_fit()
    ninth = topo.fit_point(1000)
    self.assertEqual(False, ninth)

    tenth = topo.fit_point(1)
    self.assertEqual(False, tenth)

    topo.reset_fit()
    eleventh = topo.fit_point(32)
    self.assertEqual(32, len(eleventh))
    self.assertEqual("x4211c1s1b0n0.hostmgmt2211.cm.aurora.alcf.anl.gov", eleventh[0])
    self.assertEqual("x4213c2s3b0n0.hostmgmt2213.cm.aurora.alcf.anl.gov", eleventh[31])

    topo.reset_fit()
    twelvth = topo.fit_point(33)
    self.assertEqual(False, twelvth)
 
if __name__ == '__main__':
  unittest.main()
