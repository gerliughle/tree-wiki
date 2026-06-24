from logic.Branch import Branch
from logic.Leaf import Leaf

class TreeEngine:
    all_branches = []
    all_leaves = []
    branch_map = None
    leaf_map = None

    @classmethod
    def __init__(cls):
        """ Generate the branch and leaf objects. """
        from data.Database import Database
        cls.all_branches, cls.all_leaves, cls.branch_map, cls.leaf_map = Database.read_data()
        print(f"Branches loaded: {len(cls.all_branches)}")
        print(f"Leaves loaded: {len(cls.all_leaves)}")

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
        return cls.all_leaves

    @classmethod
    def get_branches(cls):
        return cls.all_branches

    @classmethod
    def lookup_branch(cls, branch_id):
        if branch_id in cls.branch_map:
            return cls.branch_map[branch_id]
        return None

    @classmethod
    def get_care_guide(cls, branch_id):
        """ Main care guide builder. Gets leaves, checks inheritances to build new list. """

        subcategory_list = set() # subcategories that already have a leaf
        breadcrumbs = []
        care_guide = [] # list of all leaves in a care guide. Returned.
        category_list = []

        current_branch = cls.lookup_branch(branch_id)

        while current_branch is not None:
            breadcrumbs.insert(0, current_branch)
            # print(f"Checking {current_branch.name}")
            current_leaves = cls.get_leaves_for_branch(current_branch._id)

            for leaf in current_leaves:
                if leaf.subcategory not in subcategory_list:
                    subcategory_list.add(leaf.subcategory)
                    care_guide.append(leaf)
                    # print(f"Added {leaf.subcategory} to leaf guide.")
                if leaf.category not in category_list:
                    category_list.append(leaf.category)
                else:
                    # print(f"Not using {current_branch.name} {leaf.subcategory}. Subcategory already used.")
                    pass

            current_branch = cls.lookup_branch(current_branch.parent_id)
        return care_guide, breadcrumbs, category_list

    @classmethod
    def filter_phase(cls, leaves, phases):
        """ Returns a list of leaves filtered by phase.

        DEPRECATED. This should be done with JS on the page. """
        filtered_leaves = []
        print(f"Filtering list of {len(leaves)} for phases: {phases}.")
        for leaf in leaves:
            if not any(item in phases for item in leaf.phases):
                #print(f"No match found in  {leaf.subcategory}: {leaf.phases}. Removing.")
                leaves.remove(leaf)
            else:
                #print(f"Match found in {leaf.subcategory}: {leaf.phases}. Keeping.")
                filtered_leaves.append(leaf)
        print(f"Returning list filtered for phases of {len(filtered_leaves)}.\n")
        return filtered_leaves

    @classmethod
    def filter_season(cls, leaves, seasons):
        """ Returns a list of leaves filtered by season. """
        filtered_leaves = []
        print(f"Filtering list of {len(leaves)} for seasons: {seasons}.")
        for leaf in leaves:
            if not any(item in seasons for item in leaf.seasons):
                #print(f"No match found in  {leaf.subcategory}: {leaf.seasons}. Removing.")
                leaves.remove(leaf)
            else:
                #print(f"Match found in {leaf.subcategory}: {leaf.seasons}. Keeping.")
                filtered_leaves.append(leaf)
        print(f"Returning list filtered for seasons of {len(filtered_leaves)}.\n")
        return filtered_leaves

