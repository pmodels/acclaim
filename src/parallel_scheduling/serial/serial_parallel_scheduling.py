# This file disable parallel scheduling
# Use for cases where you want the microbenchmarks to run one at a time

from src.parallel_scheduling.topology import ITopology

class Topology(ITopology):
    def __init__(self):
        self.fit = False

    # Returns an array of nodes if point fits, 
    # false otherwise
    def fit_point(self, n):
        if not self.fit:
            self.fit = True
            return ['serial']
        return False
    
    # Empties topology from previous fit attempts
    def reset_fit(self):
        self.fit = False

    # Generates the topology file for the current job/allocation
    # and returns a path to the file
    @staticmethod
    def gen_topology_file(n):
        return None

    # Reads the topology file and returns a standard data structure
    @staticmethod
    def get_topology(topology_path):
        return Topology()

    # Generates a nodefile from a list of nodes (from fit_point)
    @staticmethod
    def create_nodefile(nodes, file_path):
        return None
