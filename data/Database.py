from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from configparser import ConfigParser

from data import StaticData
from data.StaticData import get_all_branches, get_all_leaves
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.User import User


class Database:
    __connection = None
    __branches = None
    __leaves = None
    __users = None

    APP_NAME = "bonsaitree"

    @classmethod
    def connect(cls):
        if cls.__connection is None:
            if "USERPROFILE" in os.environ:
                home_path = os.environ['USERPROFILE']
            elif "HOME" in os.environ:
                home_path = os.environ['HOME']
            else:
                raise Exception("Environmental variable USERPROFILE or HOME not set.")

            path = os.path.join(home_path, cls.APP_NAME)
            file = os.path.join(path, f"{cls.APP_NAME}.ini")
            if not os.path.exists(file):
                raise FileNotFoundError(f'{file} not found.')

            config_parser = ConfigParser()
            config_parser.read(file)
            username = config_parser.get("Database", "username")
            password = config_parser.get("Database", "password")
            cluster = config_parser.get("Database", "cluster")

            uri = f"mongodb+srv://{username}:{password}@{cluster}/?appName=Cluster0"
            cls.__connection = MongoClient(uri, server_api=ServerApi('1'))
            cls.__database = cls.__connection.BonsaiTree
            cls.__branches = cls.__database.Branches
            cls.__leaves = cls.__database.Leaves
            cls.__users = cls.__database.Users

    @classmethod
    def rebuild_data(cls):
        """ Returns data to original hard coded sample data, as a backup. """
        cls.connect()

        print("This will restore data to original dummy data.")
        print("Are you sure you want to continue? This is permanent. Y/N: ")
        user_input = input().lower()
        if user_input != "y":
            "Exiting."
            return
        print("Restoring data.")

        # Remake collections
        cls.__branches = cls.__database.Branches
        cls.__branches.drop()
        cls.__branches = cls.__database.Branches
        cls.__leaves.drop()
        cls.__leaves = cls.__database.Leaves
        cls.__users.drop()
        cls.__users = cls.__database.Users

        # The static data should upload dictionaries without id's.

        # Users go first, so I can save josh's id and apply it to all entries.
        all_users = StaticData.get_all_users()
        admin_id = cls.__users.insert_one(all_users[0])
        cls.__users.insert_one(all_users[1])

        # This gets all the branch dicts from StaticData.
        # As it uploads, it takes that branch's _id and sets it as parent
        # for the next branch. It collects the id's into a list to be
        # referenced when adding leaves.
        all_branches = StaticData.get_all_branches()
        parent_id = None
        id_list = []
        for branch in all_branches:
            branch['parent_id'] = parent_id
            branch['author_id'] = admin_id.inserted_id
            current_branch = cls.__branches.insert_one(branch)
            parent_id = current_branch.inserted_id
            id_list.append(current_branch.inserted_id)

        # This is more manual based on # of leaves per branch.
        all_leaves = StaticData.get_all_leaves()
        for leaf in all_leaves:
            leaf['author_id'] = admin_id.inserted_id
        for i in range(3): # 3 trunk leaves
            all_leaves[i]['branch_id'] = id_list[0]
            cls.__leaves.insert_one(all_leaves[i])
        # 0 broadleaf leaves
        for i in range(3, 5): # 2 deciduous broadleaf leaves
            all_leaves[i]['branch_id'] = id_list[2]
            cls.__leaves.insert_one(all_leaves[i])
        all_leaves[5]['branch_id'] = id_list[3]
        cls.__leaves.insert_one(all_leaves[5])
        for i in range(6, 10): # 4 JM leaves
            all_leaves[i]['branch_id'] = id_list[4]
            cls.__leaves.insert_one(all_leaves[i])

    @classmethod
    def read_data(cls):
        """ Reads data from database and builds objects. """
        cls.connect()

        branch_map ={}
        branches_dict = list(cls.__branches.find())
        branches = [Branch.build(branch, branch_map) for branch in branches_dict]

        leaf_map = {}
        leaf_dicts = list(cls.__leaves.find())
        leaves = [Leaf.build(leaf, leaf_map) for leaf in leaf_dicts]

        return branches, leaves, branch_map, leaf_map

    @classmethod
    def read_users(cls):
        cls.connect()
        users = [User.build(user) for user in cls.__users.find()]
        return users

    @classmethod
    def read_static_data(cls):
        """ Reads StaticData, and calls build methods to create objects.

        I think it gets a list of dicts, converts to objs while passing a map.

        It may be broken now, with id management."""

        branch_map = {}
        branch_dicts = get_all_branches()
        branches = [Branch.build(branch, branch_map) for branch in branch_dicts]

        leaf_map = {}
        leaf_dicts = get_all_leaves()
        leaves = [Leaf.build(leaf, leaf_map) for leaf in leaf_dicts]

        return branches, leaves, branch_map, leaf_map

    @classmethod
    def add_user(cls, username, pw_hash):
        cls.connect()
        user_dict = {
            "username": username,
            "pw_hash": pw_hash,
            "role":"user"
        }
        cls.__users.insert_one(user_dict) # mutes dict with _id
        return User.build(user_dict)

    @classmethod
    def add_branch(cls, branch_dict, branch_map):
        cls.connect()
        cls.__branches.insert_one(branch_dict)
        return Branch.build(branch_dict, branch_map)

