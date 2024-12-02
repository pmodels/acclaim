#This file deals with machine-specific parallel scheduling on ANL Polaris
#For documentation on the naming scheme of nodes on Polaris, see https://docs.alcf.anl.gov/polaris/running-jobs/

import os
import subprocess

#Basic name functions
def get_node_name(name):
    return name[:-1]

def get_rack_name(name):
    return name[1:5]

def get_dragonfly_group(name):
    return int(get_rack_name(name)) // 4

# Class representing a rack
class Rack:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.full = False

    # Gets number of nodes in the rack
    def num_nodes(self):
        return len(self.nodes)
    
    # Adds a node to the rack
    def add_node(self, node):
        node_name = get_node_name(node)
        if node_name not in self.nodes:
            self.nodes.append(node_name)

    # Checks if the rack is "full" (already assigned to a microbenchmark)
    def is_full(self):
        if self.num_nodes() == 0:
            return True
        return self.full

    # Tries to fit a microbenchmark into the rack: returns the names of 
    # the number of nodes assigned
    def fit(self, num_nodes):
        self.full = True
        if num_nodes > self.num_nodes():
            return self.nodes
        else:
            return self.nodes[:num_nodes]

    # Empties rack from previous fit attempts
    def reset_fit(self):
        self.full = False

# Class representing a dragonfly group
class DragonflyGroup:
    def __init__(self, group_name):
        self.group_name = group_name
        self.racks = []

    # Check if the requested rack is part of the dragonfly group
    def contains(self, rack_name):
        if rack_name in self.racks:
            return True
        return False

    # Add node to the group
    def add_node(self, rack_name, node_name):
        if get_dragonfly_group(node_name) == self.group_name:
            for rack in self.racks:
                if rack.name == rack_name:
                    rack.add_node(node_name)
                    return True
            new_rack = Rack(rack_name)
            new_rack.add_node(node_name)
            self.racks.append(new_rack)
            return True
        return False

    # Checks if all racks in the group are full
    def is_full(self):
        for rack in self.racks:
            if not rack.is_full():
                return False
        
        return True
        
    # Tries to fit a microbenchmark into the group: returns the names of the nodes assigned 
    def fit(self, num_nodes):
        nodes_assigned = []
        for rack in self.racks:
            if len(nodes_assigned) >= num_nodes:
               return nodes_assigned
            if not rack.is_full():
                nodes_assigned.extend(rack.fit(num_nodes - len(nodes_assigned)))

        return nodes_assigned
    
    # Empties rack pair from previous fit attempt
    def reset_fit(self):
        for rack in self.racks:
            rack.reset_fit()

        
# This class defines the topology data structure for ANL Polaris
class Topology:
    def __init__(self):
        self.dragonfly_groups = []

    # Checks if the topology contains the rack
    def contains_rack(self, rack_name):
        for group in self.dragonfly_groups:
            if(group.contains(rack_name)):
                return True
        return False

    # Adds a node to the topology
    def add_node(self, rack_name, node_name):
        for group in self.dragonfly_groups:
            if group.add_node(rack_name, node_name):
                return True
        new_group = DragonflyGroup(get_dragonfly_group(node_name))
        self.dragonfly_groups.append(new_group)
        return new_group.add_node(rack_name, node_name)

    # Attempts to fit a point into the parallel topology, returns an array of nodes if point fits, 
    # false otherwise
    def fit_point(self, num_nodes):
        nodes_assigned = []
        for group in self.dragonfly_groups:
            if len(nodes_assigned) >= num_nodes:
                return nodes_assigned
            if not group.is_full():
                nodes_assigned.extend(group.fit(num_nodes - len(nodes_assigned)))

        if len(nodes_assigned) >= num_nodes:
            return nodes_assigned
        return False

    #Empties topology from previous fit attempts
    def reset_fit(self):
        for group in self.dragonfly_groups:
            group.reset_fit()

#This function generates the topology file for the current job/allocation and returns a path to the file
def gen_topology(n):
    path_to_file = os.environ.get('PBS_NODEFILE')
    return path_to_file

#This function reads the topology file and returns a standard data structure
def get_topology(topology_path):
    topo = Topology()
    with open(topology_path) as topo_file:
        lines = topo_file.readlines()
        for line in lines:
            topo.add_node(get_rack_name(line), line)
    print("Topology loaded into memory")
    print("Found ", len(topo.dragonfly_groups), "dragonfly_groups")
    for group in topo.dragonfly_groups:
        print("  Group", group.group_name * 4, end =" ")
        for rack in group.racks:
            print("Rack", rack.name, rack.num_nodes(), end =" ")
        print("")
    return topo

# This function generates a nodefile from a list of nodes (from fit_point)
def create_nodefile(nodes, file_path):
    with open(file_path, 'w+') as f:
        for i, node in enumerate(nodes):
            if i < len(nodes)-1:
                f.write(node + "\n")
            else:
                f.write(node)