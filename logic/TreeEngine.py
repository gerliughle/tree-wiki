# from logic.Branch import Branch
# from logic.Leaf import Leaf
from bson import ObjectId


class TreeEngine:
    all_branches = []
    active_branches = []
    all_leaves = []
    active_leaves = []
    branch_map = None
    leaf_map = None

    CATEGORIES = [
        "Environment",
        "Potting",
        "Pruning",
        "Watering",
        "Fertilizing",
        "Pests and Diseases",
        "Wiring",
        "Propagation"
    ]

    @classmethod
    def __init__(cls):
        """ Generate the branch and leaf objects. """
        from data.Database import Database
        cls.active_branches, cls.active_branches, cls.branch_map, cls.active_leaves, cls.active_leaves, cls.leaf_map \
            = Database.read_data()
        print(f"Branches loaded: {len(cls.active_branches)}")
        print(f"Leaves loaded: {len(cls.active_leaves)}")

    @classmethod
    def get_leaves(cls):
        return cls.active_leaves

    @classmethod
    def get_branches(cls):
        return cls.active_branches

    @classmethod
    def get_client(cls):
        from data.Database import Database
        return Database.get_client()

    @classmethod
    def lookup_branch_by_name(cls, name):
        """ Return the Branch object by name. This is not an efficient technique. """
        name = name.strip().lower()
        for branch in cls.branch_map.values():
            if branch.name.lower() == name:
                return branch
        return None

    @classmethod
    def lookup_branch(cls, branch_id):
        if branch_id in cls.branch_map:
            return cls.branch_map[branch_id]
        return None

    @classmethod
    def get_leaves_for_branch(cls, branch_id):
        """ Return leaves that are for branch_id.
        Database is all_branches, all_leaves, branch_map, leaf_map"""
        leaf_matches = []
        for leaf in cls.active_leaves:
            if leaf.branch_id == branch_id:
                leaf_matches.append(leaf)
        return leaf_matches

    @classmethod
    def lookup_leaf(cls, leaf_id):
        if leaf_id in cls.leaf_map:
            return cls.leaf_map[leaf_id]
        return None

    @classmethod
    def get_care_guide(cls, branch_id):
        """ Main care guide builder. Gets leaves, checks inheritances to build new list. """

        subcategory_list = set()  # subcategories that already have a leaf
        breadcrumbs = []
        care_guide = []  # list of all leaves in a care guide. Returned.
        category_list = []

        current_branch = cls.lookup_branch(branch_id)

        while current_branch is not None:
            breadcrumbs.insert(0, current_branch)
            current_leaves = cls.get_leaves_for_branch(current_branch.id)

            for leaf in current_leaves:
                if leaf.subcategory not in subcategory_list:
                    subcategory_list.add(leaf.subcategory)
                    care_guide.append(leaf)
                if leaf.category not in category_list:
                    category_list.append(leaf.category)
            current_branch = cls.lookup_branch(current_branch.parent_id) # Untested

        return care_guide, breadcrumbs, category_list

    @classmethod
    def get_inherited_leaves(cls, branch_id):

        subcategory_list = set()  # subcategories that already have a leaf
        inherited_leaves = []  # list of inherited leaves only
        category_list = []

        branch = cls.lookup_branch(branch_id)
        current_branch = cls.lookup_branch(branch.id)

        while current_branch is not None:
            # print(f"Checking {current_branch.name}")
            current_leaves = cls.get_leaves_for_branch(current_branch._id)

            for leaf in current_leaves:
                if leaf.subcategory not in subcategory_list:
                    subcategory_list.add(leaf.subcategory)
                    inherited_leaves.append(leaf)
                    # print(f"Added {leaf.subcategory} to leaf guide.")

            current_branch = cls.lookup_branch(current_branch.parent_id)

        for leaf in inherited_leaves:  # remove current leaves
            if leaf.branch_id == branch_id:
                inherited_leaves.remove(leaf)

        return inherited_leaves

    @classmethod
    def get_children_of_branch(cls, branch_id):
        children_list = []
        current_branch = cls.lookup_branch(branch_id)
        for branch in cls.active_branches:
            if branch_id == branch.parent_id:
                children_list.append(branch)
        return children_list

    @classmethod
    def get_tree(cls):

        tree_builder = {}
        tree_map = []

        for branch in cls.active_branches: # creates node dict entries with empty child lists
            tree_builder[str(branch.id)] = {"node": branch, "children": []}

        for branch in cls.active_branches:
            if branch.parent_id is None: # puts roots into the actual map.
                tree_map.append(tree_builder[str(branch.id)])
            else:
                tree_builder[str(branch.parent_id)]["children"].append(tree_builder[str(branch.id)])
        return tree_map

    @classmethod
    def save_branch(cls, branch_dict, save_type):
        from data.Database import Database
        branch_id = branch_dict.get("_id", None)
        branch = Database.db_save(branch_dict, save_type, "branch", cls.branch_map)

        # This logic is for updating in-memory active lists.
        match_index = next((i for i, all_branch in enumerate(cls.active_branches) if all_branch.id == branch.id), None)
        if match_index is not None and branch.is_active:
            cls.active_branches[match_index] = branch
            print("Branch edited")
        elif branch.is_active:
            cls.active_branches.append(branch)
            print("Branch Created")
        elif not branch.is_active:
            cls.active_branches = [branch for branch in cls.active_branches if branch.id != branch_id]

        return branch

    @classmethod
    def delete_branch(cls, branch_id):
        from data.Database import Database
        delete_leaves = []
        branch_id = ObjectId(branch_id)
        delete_branch = cls.lookup_branch(branch_id)
        delete_name = delete_branch.name
        children = cls.get_children_of_branch(branch_id)

        Database.delete_branch(delete_branch, children)

        cls.active_leaves = [leaf for leaf in cls.active_leaves if leaf.branch_id != branch_id]
        cls.active_branches = [branch for branch in cls.active_branches if branch.id != branch_id]
        return delete_name


    @classmethod
    def save_leaf(cls, leaf_dict, save_type):
        from data.Database import Database
        leaf_id = leaf_dict.get("_id", None)
        leaf = Database.db_save(leaf_dict, save_type, "leaf", cls.leaf_map)

        # this check if leaf exists in all_leaves already, in case of edit vs creation.
        match_index = next((i for i, all_leaf in enumerate(cls.active_leaves) if all_leaf.id == leaf.id), None)
        if match_index is not None and leaf.is_active:
            cls.active_leaves[match_index] = leaf
            print("Leaf edited")
        elif leaf.is_active:
            cls.active_leaves.append(leaf)
            print("Leaf Created")
        elif not leaf.is_active:
            cls.active_leaves = [leaf for leaf in cls.active_leaves if leaf.id != leaf_id]
        return leaf

    @classmethod
    def delete_leaf(cls, leaf_id):
        from data.Database import Database
        delete_leaf = cls.lookup_leaf(ObjectId(leaf_id))
        Database.delete_leaf(delete_leaf)
        cls.active_leaves.remove(delete_leaf)

