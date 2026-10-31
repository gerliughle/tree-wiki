from bson import ObjectId
import os
import random
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
        print(f"Images loaded: {len(cls.image_map)}")

    @classmethod
    def read_data(cls):
        from data.Database import Database
        (cls.all_branches, cls.active_branches, cls.branch_map,
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

    @classmethod
    def get_branch_images(cls, original_id):
        """Creates list of top images for a branch.

        Only returns approved, active images.
        Limit to 5
        Sorts by quality
        If NO images, then check for children images, by generation, until there are images or out of generation
        If there are images, reprocess the list.

        """

        min_list_size = 4
        max_list_size = 6
        i = 0
        j = 0

        image_list = []
        branch_list = [cls.lookup_branch(original_id)] # branch list starts as og branch
        while len(branch_list) > 0 and len(image_list) < min_list_size: # while still children to search and haven't hit min size
            for branch in branch_list: # check og branch. then check each child in the next generation
                fetched_images = cls.fetch_branch_images([branch.id for branch in branch_list])
                for image in fetched_images:
                    if image not in image_list:
                        image_list.append(image)
                        print(f"{image_list=}")
                new_branches = cls.get_children_of_branch(branch.id)
                branch_list += new_branches
                # for new_branch in new_branches: # there shouldn't be branch dupes, right?
                #     if new_branch not in branch_list:
                #         branch_list.append(new_branch)
                branch_list.remove(branch)
                j += 1  # Individual branch incrementer
                print(f"Child image layer: {i}, child: {j}")

            i += 1  # Generation incrementer



        print(f"Search complete. Found {len(image_list)} images.")
        if len(image_list) == 0:
            print(f"No images found. Searched {j} children through {i} generations")

        if len(image_list) > max_list_size:
            print(f"More than {max_list_size} images found. ")
            if image_list[5].quality == 5: # if more than max_images images with quality of 5, restrict to those images
                print(f"More than 5 high quality images found.")
                image_list = [x for x in image_list if x.quality == 5]
                random.shuffle(image_list)
                print(f"Returning {len(image_list)} images.")

        return image_list[:max_list_size]

    @classmethod
    def fetch_branch_images(cls, branch_id_list):
        """ Gets the images for a branch and returns as a list, sorted by quality """
        approved_image_dict = {}
        print(f"Fetching images for {len(branch_id_list)} branches")
        for image in cls.active_user_images:
            if image.is_approved and image.branch_id in branch_id_list:
                approved_image_dict[image] = image.quality
        print(f"Fetched {len(approved_image_dict)} images.")
        return sorted(approved_image_dict, key=lambda x: approved_image_dict[x], reverse=True)



    @classmethod
    def delete_image(cls, image_id):
        from data.Database import Database
        from ui.WebUI import WebUI

        delete_image = cls.lookup_image(image_id)
        delete_name = delete_image.name
        path = os.path.join(WebUI.USER_IMAGES_PATH, str(delete_image.id) + delete_image.ext)
        if os.path.exists(path):
            os.remove(os.path.join(WebUI.USER_IMAGES_PATH, str(delete_image.id) + delete_image.ext))
            Database.delete_image(delete_image)
            cls.read_data()
            return delete_name
        else:
            return None