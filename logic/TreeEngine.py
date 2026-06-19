from logic.Branch import Branch
from logic.Leaf import Leaf

class TreeEngine:
    all_branches = []
    all_leaves = []
    branch_map = None
    leaf_map = None
    db = []

    @classmethod
    def __init__(cls):
        """ Generate the branch and leaf objects. """
        cls.all_branches, cls.all_leaves, cls.branch_map, cls.leaf_map = Branch.read_data()
        cls.db = Branch.read_data()
        print(f"All branches: {len(cls.all_branches)}")
        print(f"All leaves: {len(cls.all_leaves)}")
        print(f"Branch map: {len(cls.branch_map)}")
        print(f"Leaf map: {len(cls.leaf_map)}")

    @classmethod
    def lookup_branch_by_name(cls, name):
        """ Return the Branch object by name. This is not an efficient technique. """
        name = name.strip().lower()
        print(f"{name=}")
        for branch in cls.branch_map.values():
            if branch.name.lower() == name:
                print(f"Found match for '{branch.name}'")
                return branch
        return None


    @classmethod
    def get_leaves_for_branch(cls, branch_id):
        """ Return leaves that are for branch_id.

        Database is all_branches, all_leaves, branch_map, leaf_map"""
        leaf_matches = []
        for leaf in cls.all_leaves:
            if leaf.branch_id == branch_id:
                leaf_matches.append(leaf)
        return leaf_matches

    @classmethod
    def get_leaves(cls):
        return cls.all_leaves()


