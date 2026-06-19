from data.StaticData import get_all_branches, get_all_leaves
from logic.Branch import Branch
from logic.Leaf import Leaf

class Database:


    @classmethod
    def read_data(cls):
        """ Reads StaticData, and calls build methods to create objects.

        I think it gets a list of dicts, converts to objs while passing a map. """

        branch_map = {}
        branch_dicts = get_all_branches()
        branches = [Branch.build(branch, branch_map) for branch in branch_dicts]

        leaf_map = {}
        leaf_dicts = get_all_leaves()
        leaves = [Leaf.build(leaf, leaf_map) for leaf in leaf_dicts]

        return branches, leaves, branch_map, leaf_map

