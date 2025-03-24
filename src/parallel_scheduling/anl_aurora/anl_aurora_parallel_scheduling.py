#This file deals with machine-specific parallel scheduling on ANL Aurora
#For documentation on the naming scheme of nodes on Aurora, see https://docs.alcf.anl.gov/aurora/running-jobs-aurora/#placement

import os
import subprocess

from src.parallel_scheduling.topology import ITopology

#Basic name functions
def _get_node_name(name):
    return name[:-1]

def _get_chassis_name(name):
    return name[6:7]

def _get_rack_name(name):
    return name[1:5]

def _get_dragonfly_group(name):
    return int(_get_rack_name(name))

# Class representing a chassis
class Chassis:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.full = False

    # Gets number of nodes in the chassis
    def num_nodes(self):
        return len(self.nodes)
    
    # Adds a node to the chassis
    def add_node(self, node):
        node_name = _get_node_name(node)
        if node_name not in self.nodes:
            self.nodes.append(node_name)

    # Checks if the chassis is "full" (already assigned to a microbenchmark)
    def is_full(self):
        if self.num_nodes() == 0:
            return True
        return self.full

    # Tries to fit a microbenchmark into the chassis: returns the names of 
    # the number of nodes assigned
    def fit(self, num_nodes):
        self.full = True
        if num_nodes > self.num_nodes():
            return self.nodes
        else:
            return self.nodes[:int(num_nodes)]

    # Empties chassis from previous fit attempts
    def reset_fit(self):
        self.full = False

# Class representing a dragonfly group
class DragonflyGroup:
    def __init__(self, group_name):
        self.group_name = group_name
        self.chassis = []

    # Check if the requested chassis is part of the dragonfly group
    def contains(self, chassis_name):
        if chassis_name in self.chassis:
            return True
        return False

    # Add node to the group
    def add_node(self, chassis_name, node_name):
        if _get_dragonfly_group(node_name) == self.group_name:
            for chassis in self.chassis:
                if chassis.name == chassis_name:
                    chassis.add_node(node_name)
                    return True
            new_chassis = Chassis(chassis_name)
            new_chassis.add_node(node_name)
            self.chassis.append(new_chassis)
            return True
        return False

    # Checks if all chassis in the group are full
    def is_full(self):
        for chassis in self.chassis:
            if not chassis.is_full():
                return False
        
        return True
        
    # Tries to fit a microbenchmark into the group: returns the names of the nodes assigned 
    def fit(self, num_nodes):
        nodes_assigned = []
        for chassis in self.chassis:
            if len(nodes_assigned) >= num_nodes:
               return nodes_assigned
            if not chassis.is_full():
                nodes_assigned.extend(chassis.fit(num_nodes - len(nodes_assigned)))

        return nodes_assigned
    
    # Empties the group from previous fit attempt
    def reset_fit(self):
        for chassis in self.chassis:
            chassis.reset_fit()

        
# This class defines the topology data structure for ANL Polaris
class Topology(ITopology):
    def __init__(self):
        self.dragonfly_groups = []

    # Adds a node to the topology
    def _add_node(self, chassis_name, node_name):
        for group in self.dragonfly_groups:
            if group.add_node(chassis_name, node_name):
                return True
        new_group = DragonflyGroup(_get_dragonfly_group(node_name))
        self.dragonfly_groups.append(new_group)
        return new_group.add_node(chassis_name, node_name)

    # Returns an array of nodes if point fits, 
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

    # Empties topology from previous fit attempts
    def reset_fit(self):
        for group in self.dragonfly_groups:
            group.reset_fit()

    # Generates the topology file for the current job/allocation
    # and returns a path to the file
    @staticmethod
    def gen_topology_file(n):
        path_to_file = os.environ.get('PBS_NODEFILE')
        return path_to_file

    # Reads the topology file and returns a standard data structure
    @staticmethod
    def get_topology(topology_path):
        topo = Topology()
        with open(topology_path) as topo_file:
            lines = topo_file.readlines()
            for line in lines:
                topo._add_node(_get_chassis_name(line), line)
        print("Topology loaded into memory")
        print("Found ", len(topo.dragonfly_groups), "dragonfly_groups")
        for group in topo.dragonfly_groups:
            print("  Group", group.group_name * 4, end =" ")
            for chassis in group.chassis:
                print("Chassis", chassis.name, chassis.num_nodes(), end =" ")
            print("")
        return topo

    # Generates a nodefile from a list of nodes (from fit_point)
    @staticmethod
    def create_nodefile(nodes, file_path):
        with open(file_path, 'w+') as f:
            for i, node in enumerate(nodes):
                if i < len(nodes)-1:
                    f.write(node + "\n")
                else:
                    f.write(node)
        return file_path