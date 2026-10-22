from bson import ObjectId

from logic.Validate import Validate


class TreeEngine:
    all_branches = []
    active_branches = []
    branch_map = None
    all_leaves = []
    active_leaves = []
    leaf_map = None
    user_images = []
    active_user_images = []
    image_map = None

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
        cls.read_data()
        print(f"Branches loaded: {len(cls.active_branches)}")
        print(f"Leaves loaded: {len(cls.active_leaves)}")

    @classmethod
    def read_data(cls):
        from data.Database import Database
        (cls.active_branches, cls.active_branches, cls.branch_map,
         cls.active_leaves, cls.active_leaves, cls.leaf_map,
         cls.user_images, cls.active_user_images, cls.image_map) \
            = Database.read_data()


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
        # branch_id = Validate.make_objectid(branch_id)
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
        # leaf_id = Validate.make_objectid(leaf_id)
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
                if not (leaf.end_chain is True and len(breadcrumbs) > 1):

                    if leaf.subcategory not in subcategory_list:
                        subcategory_list.add(leaf.subcategory)
                        care_guide.append(leaf)
                    if leaf.category not in category_list:
                        category_list.append(leaf.category)
            current_branch = cls.lookup_branch(current_branch.parent_id)

        return care_guide, breadcrumbs, category_list

    @classmethod
    def get_children_of_branch(cls, branch_id):
        children_list = []

        # branch_id = Validate.make_objectid(branch_id)
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
        branch = Database.db_save(branch_dict, save_type, "branch", cls.branch_map)
        cls.read_data()
        return branch

    @classmethod
    def delete_branch(cls, branch_id):
        from data.Database import Database
        delete_leaves = []
        # branch_id = Validate.make_objectid(branch_id)
        delete_branch = cls.lookup_branch(branch_id)
        delete_name = delete_branch.name
        children = cls.get_children_of_branch(branch_id)

        Database.delete_branch(delete_branch, children)

        cls.read_data()
        return delete_name


    @classmethod
    def save_leaf(cls, leaf_dict, save_type):
        from data.Database import Database
        leaf = Database.db_save(leaf_dict, save_type, "leaf", cls.leaf_map)
        cls.read_data()
        return leaf

    @classmethod
    def delete_leaf(cls, leaf_id):
        from data.Database import Database
        # leaf_id = Validate.make_objectid(leaf_id)
        delete_leaf = cls.lookup_leaf(ObjectId(leaf_id))
        Database.delete_leaf(delete_leaf)
        cls.read_data()

    @classmethod
    def lookup_image(cls, image_id):
        if image_id in cls.image_map:
            return cls.image_map[image_id]
        return None

    @classmethod
    def save_image(cls, img_dict, save_type):
        """ Take a new image, create database entry, name & save image."""
        from data.Database import Database
        user_image = Database.db_save(img_dict, save_type, "image", cls.image_map)

        cls.read_data()
        return user_image

    @classmethod
    def get_active_user_images(cls):
        return cls.active_user_images

    @classmethod
    def get_all_user_images(cls):
        return cls.user_images
