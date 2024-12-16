from abc import ABC, abstractmethod

class ITopology(ABC):
    @abstractmethod
    def fit_point(self, n):
        """ Check and return an array of nodes if the point fits, false otherwise. """
        pass

    @abstractmethod
    def reset_fit(self):
        """ Empties topology from previous fit attempts. """
        pass

    @staticmethod
    @abstractmethod
    def gen_topology_file(self, n):
        """ Generates the topology file for the current job/allocation and returns the path to the file. """
        pass

    @staticmethod
    @abstractmethod
    def get_topology(self, topology_path):
        """ Reads the topology file and returns a standard data structure. """
        pass

    @staticmethod
    @abstractmethod
    def create_nodefile(self, nodes, file_path):
        """ Generates a nodefile from a list of nodes. """
        pass
