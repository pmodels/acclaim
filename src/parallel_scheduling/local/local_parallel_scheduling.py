# This file deals with parallel scheduling for a local system
# The local scheduler allows for INFINITE PARALLEL SCHEDULING
# This implementation is provided FOR TESTING PURPOSES ONLY

from src.parallel_scheduling.topology import ITopology

class Topology(ITopology):
    # Returns an array of nodes if point fits, 
    # false otherwise
    def fit_point(self, n):
        return ['local']
    
    # Empties topology from previous fit attempts
    def reset_fit(self):
        return

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