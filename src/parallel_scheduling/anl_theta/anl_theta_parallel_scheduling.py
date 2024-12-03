#This file deals with machine-specific parallel scheduling for ANL Theta

import os
import subprocess
from src.user_config.config_manager import ConfigManager

#This class defines the topology data structure for ANL Theta
class Topology:
    def __init__(self):
        self.rack_pairs = []

    #Checks if the topology contains the rack
    def contains_rack(self, rack_name):
        for rack_pair in self.rack_pairs:
            if(rack_pair.contains(rack_name)):
                return True
        return False

    #Adds a rack to the topology
    def add_rack(self, rack_name):
        if(not self.contains_rack(rack_name)):
            self.rack_pairs.append(self.RackPair(rack_name))

    #Adds a node to the topology
    def add_node(self, rack_name, node_name):
        if(not self.contains_rack(rack_name)):
            self.add_rack(rack_name)
        for rack_pair in self.rack_pairs:
            if(rack_pair.contains(rack_name)):
                return rack_pair.add_node(rack_name, node_name)
                
        print("Error: does not contain rack")
        return False

    #Attempts to fit a point into the parallel topology, returns True if point fits, false otherwise
    def fit_point(self, num_nodes):
        unassigned_nodes = num_nodes
        for rack_pair in self.rack_pairs:
            if(not rack_pair.is_full()):
                num_fit_in_rack_pair = rack_pair.fit(unassigned_nodes)
                unassigned_nodes -= num_fit_in_rack_pair
                if(unassigned_nodes == 0):
                    return True
        return False

    #Empties topology from previous fit attempts
    def reset_fit(self):
        for rack_pair in self.rack_pairs:
            rack_pair.reset_fit()

    #Inner class representing rack pairs
    class RackPair:
        def __init__(self, rack_name):
            #Logic for determining rack pairs by name
            rack_number = rack_name % 10
            if(rack_number % 2):
                self.rack1 = self.Rack(rack_name - 10)
                self.rack2 = self.Rack(rack_name)
            else:
                self.rack1 = self.Rack(rack_name)
                self.rack2 = self.Rack(rack_name + 10)
        
        #Check if the requested rack is part of the rack pair
        def contains(self, rack_name):
            if self.rack1.name == rack_name or self.rack2.name == rack_name:
                return True
            return False

        #add node to the appropriate rack in pair
        def add_node(self, rack_name, node_name):
            if(self.rack1.name == rack_name):
                self.rack1.add_node(node_name)
                return True
            elif(self.rack2.name == rack_name):
                self.rack2.add_node(node_name)
                return True
            return False

        #checks if both racks in pair are full
        def is_full(self):
            if(self.rack1.is_full() and self.rack2.is_full()):
                return True
            else:
                return False
            
        #tries to fit a microbenchmark into the rack pair: returns the number of nodes remaining unassigned 
        def fit(self, num_nodes):
            num_nodes_to_assign = num_nodes
            num_fit_in_rack_pair = 0
            if(not self.rack1.is_full()):
                num_fit_in_rack_pair += self.rack1.fit(num_nodes_to_assign)
                if(num_fit_in_rack_pair == num_nodes_to_assign):
                    return num_fit_in_rack_pair
                num_nodes_to_assign -= num_fit_in_rack_pair
            if(not self.rack2.is_full()):
                num_fit_in_rack_pair += self.rack2.fit(num_nodes_to_assign)

            return num_fit_in_rack_pair
        
        #empties rack pair from previous fit attempt
        def reset_fit(self):
            self.rack1.reset_fit()
            self.rack2.reset_fit()

        #Inner inner class representing a rack
        class Rack:
            def __init__(self, name):
                self.name = name
                self.nodes = []
                self.full = False

            #gets number of nodes in the rack for our topology
            def num_nodes(self):
                return len(self.nodes)
            
            #adds a node to the rack
            def add_node(self, node):
                if(node not in self.nodes):
                    self.nodes.append(node)

            #checks if the rack is "full" (already assigned to a microbenchmark)
            def is_full(self):
                if(self.num_nodes() == 0):
                    return True
                return self.full

            #tries to fit a microbenchmark into the rack: returns the number of nodes remaining unassigned
            def fit(self, num_nodes):
                self.full = True
                if(num_nodes > self.num_nodes()):
                    return self.num_nodes()
                else:
                    return num_nodes

            #empties rack from previous fit attempts
            def reset_fit(self):
                self.full = False

def get_rack_name_from_line(line):
    equals_index = line.find("cname = ")
    dash_index = line.find('-')
    if(dash_index == -1):
        return -1
    rack_name = int(line[dash_index-1] + line[dash_index+1])
    return rack_name

def get_node_name_from_line(line):
    equals_index = line.find("cname = ")
    node_name = str(line[equals_index+8:]).rstrip()
    return node_name

#This function generates the topology file for the current job/allocation and returns a path to the file
def gen_topology(n):
    root_path = ConfigManager.get_instance().get_value('settings', 'acclaim_root')
    topo_test_path = root_path + '/fact/src/parallel_scheduling/anl_theta/aries-topo/src/test'
    with open("topo.out", "w") as f:
      subprocess.run(["aprun", "-n", str(n), topo_test_path], stdout=f)
    topo_out_path = os.getcwd() + '/topo.out'
    return topo_out_path

#This function reads the topology file and returns a standard data structure
def get_topology(topology_path):
    topo = Topology()
    with open(topology_path) as topo_file:
        lines = topo_file.readlines()
        for line in lines:
            if "/proc/cray_xt/cname = " in line:
                node_name = get_node_name_from_line(line)
                rack_name = get_rack_name_from_line(node_name)
                if(rack_name == -1 or node_name.count("c") != 2 or node_name.count("s") != 1 or node_name.count("n") != 1):
                    continue
                topo.add_rack(rack_name)
                success = topo.add_node(rack_name, node_name)
                if(not success):
                    print("Error: failed to add node")
    print("Topology loaded into memory")
    print("Found ", len(topo.rack_pairs), "rack pairs")
    for pair in topo.rack_pairs:
        print(pair.rack1.num_nodes(), pair.rack2.num_nodes())
        print(pair.rack1.nodes, pair.rack2.nodes)
    return topo

