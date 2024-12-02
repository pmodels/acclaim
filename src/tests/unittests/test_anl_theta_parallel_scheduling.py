# This file tests "anl_theta_parallel_scheduling.py" using unittest
import unittest

import os
import sys
import json
import numpy as np

from src.parallel_scheduling.anl_theta.anl_theta_parallel_scheduling import Topology, get_rack_name_from_line, get_node_name_from_line, get_topology

class TestParallelScheduling(unittest.TestCase):
  def test_rack_name(self):
    line = "0: /proc/cray_xt/cname = c5-1c1s3n1"
    result = get_rack_name_from_line(line)
    correct = 51
    self.assertEqual(result,correct)

  def test_node_name(self):
    line = "11: /proc/cray_xt/cname = c6-0c1s3n1" 
    result = get_node_name_from_line(line)
    correct = "c6-0c1s3n1"
    self.assertEqual(result,correct)
    line = '11: /proc/cray_xt/cname = c6-0c1s3n1 \n'
    result = get_node_name_from_line(line)
    correct = "c6-0c1s3n1"
    self.assertEqual(result,correct)
  
  def test_get_topology_simple(self):
    pwd = os.getcwd()
    simple_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_simple.output'   #51 and 60
    topo = get_topology(simple_topo_path)
    self.assertEqual(2, len(topo.rack_pairs))
    self.assertEqual(41,topo.rack_pairs[0].rack1.name)
    self.assertEqual(51,topo.rack_pairs[0].rack2.name)
    self.assertEqual(60,topo.rack_pairs[1].rack1.name)
    self.assertEqual(70,topo.rack_pairs[1].rack2.name)
    self.assertEqual(0, len(topo.rack_pairs[0].rack1.nodes))
    self.assertEqual(1, len(topo.rack_pairs[0].rack2.nodes))
    self.assertEqual(1, len(topo.rack_pairs[1].rack1.nodes))
    self.assertEqual(0, len(topo.rack_pairs[1].rack2.nodes))
    self.assertEqual("c5-1c1s3n1", topo.rack_pairs[0].rack2.nodes[0])
    self.assertEqual("c6-0c1s3n1", topo.rack_pairs[1].rack1.nodes[0])
  
  def test_get_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_example.output'
    topo = get_topology(example_topo_path)
    self.assertEqual(2, len(topo.rack_pairs))
    self.assertEqual(41,topo.rack_pairs[0].rack1.name)
    self.assertEqual(51,topo.rack_pairs[0].rack2.name)
    self.assertEqual(61,topo.rack_pairs[1].rack1.name)
    self.assertEqual(71,topo.rack_pairs[1].rack2.name)
    self.assertEqual(0, topo.rack_pairs[0].rack1.num_nodes())
    self.assertEqual(1, topo.rack_pairs[0].rack2.num_nodes())
    self.assertEqual(6, topo.rack_pairs[1].rack1.num_nodes())
    self.assertEqual(9, topo.rack_pairs[1].rack2.num_nodes())
    self.assertEqual(1, topo.rack_pairs[0].rack2.nodes.count("c5-1c1s3n1"))
    self.assertEqual(1, topo.rack_pairs[1].rack1.nodes.count("c6-1c1s1n3"))
    self.assertEqual(1, topo.rack_pairs[1].rack1.nodes.count("c6-1c2s6n2"))
    self.assertEqual(1, topo.rack_pairs[1].rack2.nodes.count("c7-1c0s0n3"))
   
  def test_get_topology_huge(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_huge.output'
    topo = get_topology(example_topo_path)
    #print(topo.rack_pairs[0].rack1)
    #print(topo.rack_pairs[0].rack1.nodes)
    #print(topo.rack_pairs[0].rack2)
    #print(topo.rack_pairs[0].rack2.nodes)
    self.assertEqual(2, len(topo.rack_pairs))
    self.assertEqual(0, len(topo.rack_pairs[0].rack1.nodes))
    self.assertEqual(19, len(topo.rack_pairs[0].rack2.nodes))
    self.assertEqual(0, len(topo.rack_pairs[1].rack1.nodes))
    self.assertEqual(13, len(topo.rack_pairs[1].rack2.nodes))
  
  def test_get_topology_gigantic(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_gigantic.output'
    topo = get_topology(example_topo_path)
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_gigantic2.output'
    topo = get_topology(example_topo_path)
    #print(topo.rack_pairs[0].rack1)
    #print(topo.rack_pairs[0].rack1.nodes)
    #print(topo.rack_pairs[0].rack2)
    #print(topo.rack_pairs[0].rack2.nodes)
    #self.assertEqual(2, len(topo.rack_pairs))
    #self.assertEqual(0, len(topo.rack_pairs[0].rack1.nodes))
    #self.assertEqual(19, len(topo.rack_pairs[0].rack2.nodes))
    #self.assertEqual(0, len(topo.rack_pairs[1].rack1.nodes))
    #self.assertEqual(13, len(topo.rack_pairs[1].rack2.nodes))
  
  def test_fit_topology_simple(self):
    pwd = os.getcwd()
    simple_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_simple.output'   #51 and 60
    topo = get_topology(simple_topo_path)
    first = topo.fit_point(1)
    second = topo.fit_point(1)
    third = topo.fit_point(1)
    topo.reset_fit()
    fourth = topo.fit_point(2)
    fifth = topo.fit_point(1)
    self.assertEqual(True, first)
    self.assertEqual(True, second)
    self.assertEqual(False, third)
    self.assertEqual(True, fourth)
    self.assertEqual(False, fifth)
  
  def test_fit_topology_complex(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_example.output'
    topo = get_topology(example_topo_path)
    first = topo.fit_point(7)
    second = topo.fit_point(3)
    third = topo.fit_point(2)
    topo.reset_fit()
    fourth = topo.fit_point(16)
    fifth = topo.fit_point(1)
    topo.reset_fit()
    sixth = topo.fit_point(1)
    seventh = topo.fit_point(6)
    eighth = topo.fit_point(9)
    ninth = topo.fit_point(1000)
    self.assertEqual(True, first)
    self.assertEqual(True, second)
    self.assertEqual(False, third)
    self.assertEqual(True, fourth)
    self.assertEqual(False, fifth)
    self.assertEqual(True, sixth)
    self.assertEqual(True, seventh)
    self.assertEqual(True, eighth)
    self.assertEqual(False, ninth)
  
  def test_fit_topology_huge(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_huge.output'
    topo = get_topology(example_topo_path)
    first = topo.fit_point(19)
    second = topo.fit_point(12)
    third = topo.fit_point(2)
    topo.reset_fit()
    fourth = topo.fit_point(32)
    fifth = topo.fit_point(1)
    topo.reset_fit()
    #sixth = topo.fit_point(1)
    #seventh = topo.fit_point(6)
    #eighth = topo.fit_point(9)
    #ninth = topo.fit_point(1000)
    self.assertEqual(True, first)
    self.assertEqual(True, second)
    self.assertEqual(False, third)
    self.assertEqual(True, fourth)
    self.assertEqual(False, fifth)
    #self.assertEqual(True, sixth)
    #self.assertEqual(True, seventh)
    #self.assertEqual(True, eighth)
    #self.assertEqual(False, ninth)
    
  def test_fit_topology_gigantic(self):
    pwd = os.getcwd()
    example_topo_path = pwd + '/src/tests/unittests/theta_topos/anl_theta_topo_output_gigantic.output'
    topo = get_topology(example_topo_path)
    first = topo.fit_point(2)
    second = topo.fit_point(2)
    third = topo.fit_point(200000)
    topo.reset_fit()
    fourth = topo.fit_point(32)
    fifth = topo.fit_point(32)
    sixth = topo.fit_point(32)
    seventh = topo.fit_point(128)
    eighth = topo.fit_point(128)
    ninth = topo.fit_point(128)
    topo.reset_fit()
    self.assertEqual(True, first)
    self.assertEqual(True, second)
    self.assertEqual(False, third)
    self.assertEqual(True, fourth)
    self.assertEqual(True, fifth)
    self.assertEqual(True, sixth)
    self.assertEqual(False, seventh)
    self.assertEqual(False, eighth)
    self.assertEqual(False, ninth)
    
if __name__ == '__main__':
  unittest.main()
