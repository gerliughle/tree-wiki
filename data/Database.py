from flask_login import current_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument
import os
from configparser import ConfigParser
from bson import ObjectId
from datetime import datetime, timezone

from data import StaticData
from data.StaticData import get_all_branches, get_all_leaves
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.User import User
from logic.TreeEngine import TreeEngine


class Database:
    __connection = None
    __branches = None
    __leaves = None
    __users = None
    __audit_log = None

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
            cls.__audit_log = cls.__database.AuditLog

    @classmethod
    def rebuild_data(cls):
        """ Returns data to original hard coded sample data, as a backup. """
        cls.connect()

        print("This will restore data to original dummy data.")
        print("Are you sure you want to continue? This is permanent. Mongo Backup and Restore is preferred. Y/N: ")
        user_input = input().lower()
        if user_input != "y":
            "Exiting."
            exit()
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
        for i in range(3):  # 3 trunk leaves
            all_leaves[i]['branch_id'] = id_list[0]
            cls.__leaves.insert_one(all_leaves[i])
        # 0 broadleaf leaves
        for i in range(3, 5):  # 2 deciduous broadleaf leaves
            all_leaves[i]['branch_id'] = id_list[2]
            cls.__leaves.insert_one(all_leaves[i])
        all_leaves[5]['branch_id'] = id_list[3]
        cls.__leaves.insert_one(all_leaves[5])
        for i in range(6, 10):  # 4 JM leaves
            all_leaves[i]['branch_id'] = id_list[4]
            cls.__leaves.insert_one(all_leaves[i])

    @classmethod
    def read_data(cls):
        """ Reads data from database and builds objects. """
        cls.connect()

        branch_map = {}
        branches_dict = list(cls.__branches.find())
        branches = [Branch.build(branch, branch_map) for branch in branches_dict]

        leaf_map = {}
        leaf_dicts = list(cls.__leaves.find())
        leaves = [Leaf.build(leaf, leaf_map) for leaf in leaf_dicts]

        return branches, leaves, branch_map, leaf_map

    @classmethod
    def read_users(cls):
        cls.connect()
        user_dict = list(cls.__users.find())
        users = [User.build(user) for user in user_dict]
        return users

    @classmethod
    def read_audit(cls):
        cls.connect()
        return cls.__audit_log

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
    def save_user(cls, user_dict):
        cls.connect()
        print(f"Debug. {user_dict=}")
        # Dict either has ID, and I edit, or no ID, and I create.
        query_filter = {}
        if user_dict.get("_id", False):
            query_filter["_id"] = user_dict["_id"]
            user_dict.pop("_id")
            editor_id = current_user.id
            editor_username = current_user.username
            task = "Edit User"
        else:
            new_id = ObjectId()
            query_filter["_id"] = new_id
            task = "Register User"
            editor_id = new_id
            editor_username = user_dict["username"]

        if not user_dict.get("role", False):
            user_dict["role"] = "user"

        update_payload = {
            "$set": user_dict
        }

        new_user_doc = cls.__users.find_one_and_update(query_filter,
                                                       update_payload,
                                                       upsert=True,
                                                       return_document=ReturnDocument.AFTER)

        log_user_dict = user_dict.copy()
        log_user_dict.pop("pw_hash", None)

        log_payload = {
            "timestamp": datetime.now(timezone.utc),
            "user_id": editor_id,
            "username": editor_username,
            "target_id": new_user_doc["_id"],
            "target_name": new_user_doc["username"],
            "task": task,
            "edit": log_user_dict
        }
        print(f"{log_payload=}")
        cls.update_log(log_payload)

        return User.build(new_user_doc)

    @classmethod
    def delete_user(cls, user):
        cls.connect()

        delete_doc = cls.__users.delete_one({"_id": user.id})
        if delete_doc.acknowledged:
            print("Deleted user")
            log_payload = {
                "timestamp": datetime.now(timezone.utc),
                "user_id": current_user.id,
                "username": current_user.username,
                "target_id": user.id,
                "target_name": user.username,
                "task": "Delete User",
                "edit": {
                    "deleted_user_id": user.id,
                    "deleted_username": user.username
                }
            }
            print(f"{log_payload=}")
            cls.update_log(log_payload)
        else:
            print("Did not complete user deletion.")

    @classmethod
    def lookup_user(cls, attr, value):
        cls.connect()
        user_doc = cls.__users.find_one({attr: value})
        if user_doc:
            return User.build(user_doc)
        else:
            return None


    @classmethod
    def update_log(cls, payload):
        """ Updates the audit log """
        cls.connect()
        log = cls.__audit_log.insert_one(payload)
        timestamp = payload.get("timestamp")

        if timestamp:
            formatted_date = timestamp.strftime("%Y-%m-%d")
            formatted_time = timestamp.strftime("%H:%M:%S")
            print(f"Log Updated at {formatted_date} - {formatted_time}")


    @classmethod
    def save_branch(cls, branch_dict, branch_map):
        """ This either saves or creates a new branch. """
        cls.connect()

        # I receive a dict wtih either no id, and the dict to create
        # or, an id and changes.
        query_filter = {}
        if branch_dict.get("_id", False):
            query_filter["_id"] = branch_dict["_id"]
            branch_dict.pop("_id")
            task = "Edit Branch"
        else:
            query_filter["_id"] = ObjectId()
            task = "Create Branch"

        update_payload = {
            "$set": branch_dict
        }

        new_branch_doc = cls.__branches.find_one_and_update(query_filter,
                                                            update_payload,
                                                            upsert=True,
                                                            return_document=ReturnDocument.AFTER)

        log_payload = {
            "timestamp": datetime.now(timezone.utc),
            "user_id": current_user.id,
            "username": current_user.username,
            "target_id": new_branch_doc["_id"],
            "target_name": new_branch_doc["name"],
            "task": task,
            "edit": branch_dict
        }
        # print(f"{log_payload=}")
        cls.update_log(log_payload)

        return Branch.build(new_branch_doc, branch_map)



    @classmethod
    def delete_branch(cls, branch, children):
        cls.connect()

        # Update db, set children's parents to branch's parent
        cls.__branches.update_many(
            {"parent_id": branch.id},
            {"$set": {"parent_id": branch.parent_id}}
        )

        # Delete all the leaves from the branch
        cls.__leaves.delete_many({"branch_id": branch.id})

        # Update the in-memory objects from user session.
        if children:
            for child in children:
                setattr(child, "parent_id", branch.parent_id)

        # Delete the branch and provide a delete_doc
        delete_doc = cls.__branches.delete_one({"_id": branch.id})

        if delete_doc.acknowledged:
            print("Deleted branch")
            log_payload = {
                "timestamp": datetime.now(timezone.utc),
                "user_id": current_user.id,
                "username": current_user.username,
                "target_id": branch.id,
                "target_name": branch.name,
                "task": "Delete Branch",
                "edit": {
                    # "deleted_branch_id": branch.id,
                    # "deleted_branch_name": branch.name,
                    # "new_parent_id": branch.parent_id
                    "impacted_children": children
                }
            }
            # print(f"{log_payload=}")
            cls.update_log(log_payload)
        else:
            print("Did not complete branch deletion.")

    @classmethod
    def save_leaf(cls, leaf_dict, leaf_map):
        """ This uses a filter to see if there is a leaf with the same branch, cat and subcat. If not, it adds, if so, it edits. """
        cls.connect()

        query_filter = {
            "branch_id": leaf_dict["branch_id"],
            "category": leaf_dict["category"],
            "subcategory": leaf_dict["subcategory"],
        }

        # Replaces everything else.
        update_payload = {
            "$set": {
                "author_id": leaf_dict["author_id"],
                "branch_id": leaf_dict["branch_id"],
                "seasons": leaf_dict["seasons"],
                "entries": leaf_dict["entries"]
            }
        }

        new_leaf_doc = cls.__leaves.find_one_and_update(query_filter,
                                                        update_payload,
                                                        upsert=True,
                                                        return_document=ReturnDocument.AFTER)

        log_payload = {
            "timestamp": datetime.now(timezone.utc),
            "user_id": current_user.id,
            "username": current_user.username,
            "target_id": new_leaf_doc["_id"],
            "target_name": new_leaf_doc["subcategory"],
            "task": "Create/Edit Leaf",
            "edit": leaf_dict
        }
        print(f"{log_payload=}")
        cls.update_log(log_payload)

        return Leaf.build(new_leaf_doc, leaf_map)

    @classmethod
    def delete_leaf(cls, leaf):
        cls.connect()
        delete_doc = cls.__leaves.delete_one({"_id": leaf.id})
        if delete_doc.acknowledged:
            print("Deleted leaf")
            log_payload = {
                "timestamp": datetime.now(timezone.utc),
                "user_id": current_user.id,
                "username": current_user.username,
                "target_id": leaf.id,
                "target_name": leaf.subcategory,
                "task": "Delete Leaf",
                "edit": {
                    "deleted_leaf_id": leaf.id,
                    "deleted_leaf_entries": leaf.entries
                }
            }
            print(f"{log_payload=}")
            cls.update_log(log_payload)
        else:
            print("Did not complete leaf deletion.")

    @classmethod
    def rebuild_leaves(cls):
        """ Migrates leaf object data to support entries feature. Only run once (ideally). """
        cls.connect()
        all_leaves = list(cls.__leaves.find())

        for leaf_dict in all_leaves:
            if "phases" not in leaf_dict or "text" not in leaf_dict:
                continue

            entries = [
                {
                    "text": leaf_dict["text"],
                    "phases": leaf_dict["phases"]
                }
            ]
            cls.__leaves.update_one(
                {"_id": leaf_dict["_id"]},
                {
                    "$set": {"entries": entries},
                    "$unset": {"text": "", "phases": ""}
                }
            )

    @classmethod
    def migration_error_check(cls):
        cls.connect()
        all_leaves = list(cls.__leaves.find())

        for leaf_dict in all_leaves:
            for leaf_check in all_leaves:
                if leaf_dict["subcategory"] == leaf_check["subcategory"] \
                        and leaf_dict["category"] == leaf_check["category"] \
                        and leaf_dict["_id"] != leaf_check["_id"] \
                        and leaf_dict["branch_id"] == leaf_check["branch_id"]:
                    print(f"Error found? {leaf_dict['_id']} conflict with {leaf_check['_id']}")
