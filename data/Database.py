from flask_login import current_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import ReturnDocument
import os
from configparser import ConfigParser
from bson import ObjectId
from datetime import datetime, timezone

# from data import StaticData
# from data.StaticData import get_all_branches, get_all_leaves
from logic.Branch import Branch
from logic.Leaf import Leaf
from logic.User import User
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager


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
            home_path = os.environ['HOME']
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
    def get_client(cls):
        return cls.__connection

    @classmethod
    def read_data(cls):
        """ Reads data from database and builds objects. """
        cls.connect()

        branch_map = {}
        branches_dict = list(cls.__branches.find())
        branches = [Branch.build(branch, branch_map) for branch in branches_dict]
        active_branches = [branch for branch in branches if branch.is_active]

        leaf_map = {}
        leaf_dicts = list(cls.__leaves.find({"is_active": True}))
        leaves = [Leaf.build(leaf, leaf_map) for leaf in leaf_dicts]
        active_leaves = [leaf for leaf in leaves if leaf.is_active]

        return branches, active_branches, branch_map, leaves, active_leaves, leaf_map

    @classmethod
    def read_users(cls):
        cls.connect()
        user_dict = list(cls.__users.find())
        users = [User.build(user) for user in user_dict]
        return users

    @classmethod
    def read_audit(cls): # FIXME is this unused?
        cls.connect()
        return cls.__audit_log

    @classmethod
    def get_audit_log(cls):
        audit_dict = list(cls.__audit_log.find())
        return audit_dict

    @classmethod
    def get_audit_entry(cls, entry_id):
        audit_entry = cls.__audit_log.find_one({"_id": ObjectId(entry_id)})
        return audit_entry

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
    def db_save(cls, save_dict, save_type, obj_type, obj_map=None):
        """ Single save method that should allow all create/edit/disable/enable routing to one spot

        Rather than figuring it out by analyzing the dict, just ask the caller.
        save_dict should have _id if existing, if not it will create. otherwise have all changes
        save_type should be "create", "edit", "disable", enable"
        obj_type should be "user", "branch" or "leaf"
        Deleting is handled separately.
        """

        query_filter = {}
        save_obj = None
        obj_name = ""
        obj_db = None
        current_user_id = None
        current_username = ""


        cls.connect()
        print(f"Processing save request.")
        print(f"{save_type=} {obj_type=}")


        if save_type == "create":
            query_filter["_id"] = ObjectId()
        else:
            save_id = save_dict["_id"]
            query_filter["_id"] = save_id
            save_dict.pop("_id")
            if obj_type == "user":
                save_obj = UserManager.lookup_user_id(save_id)
            elif obj_type == "branch":
                save_obj = TreeEngine.lookup_branch(save_id)
            elif obj_type == "leaf":
                save_obj = TreeEngine.lookup_leaf(save_id)
            obj_name = save_obj.name

        if obj_type == "user":
            obj_db = cls.__users
        if obj_type == "branch":
            obj_db = cls.__branches
        if obj_type == "leaf":
            obj_db = cls.__leaves

        update_payload = {
            "$set": save_dict
        }

        new_obj_doc = obj_db.find_one_and_update(
            query_filter,
            update_payload,
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        if "pw_hash" in save_dict:
            save_dict["pw_hash"] = "HASH REDACTED"

        if not current_user.is_active:
            current_user_id = new_obj_doc["_id"]
            current_username = new_obj_doc["username"]
        else:
            current_user_id = current_user.id
            current_username = current_user.username

        log_payload = {
            "timestamp": datetime.now(timezone.utc),
            "user_id": current_user_id,
            "username": current_username,
            "target_id": new_obj_doc["_id"],
            "target_name": obj_name,
            "task": save_type.title(),
            "obj_type": obj_type.title(),
            "edit": {
                "after": save_dict,
                "before": {}
            }
        }

        if save_obj:
            for edit in save_dict:
                log_payload["edit"]["before"][edit] = (getattr(save_obj, edit))

        cls.update_log(log_payload)
        if obj_type == "user":
            print("Successfully updated user.")
            return User.build(new_obj_doc)
        elif obj_type == "branch":
            print("Successfully updated branch.")
            return Branch.build(new_obj_doc, obj_map)
        elif obj_type == "leaf":
            print("Successfully updated leaf.")
            return Leaf.build(new_obj_doc, obj_map)
        print("Error, did not complete save method.")
        return None


    #
    #
    #
    # @classmethod
    # def save_user(cls, user_dict):
    #     cls.connect()
    #     print(f"Debug. {user_dict=}")
    #     # Dict either has ID, and I edit, or no ID, and I create.
    #     query_filter = {}
    #     if user_dict.get("_id", False):
    #         query_filter["_id"] = user_dict["_id"]
    #         user_dict.pop("_id")
    #         editor_id = current_user.id
    #         editor_username = current_user.username
    #         task = "Edit User"
    #     else:
    #         new_id = ObjectId()
    #         query_filter["_id"] = new_id
    #         task = "Register User"
    #         editor_id = new_id
    #         editor_username = user_dict["username"]
    #
    #     if not user_dict.get("role", False):
    #         user_dict["role"] = "user"
    #
    #     update_payload = {
    #         "$set": user_dict
    #     }
    #
    #     new_user_doc = cls.__users.find_one_and_update(query_filter,
    #                                                    update_payload,
    #                                                    upsert=True,
    #                                                    return_document=ReturnDocument.AFTER)
    #
    #     log_user_dict = user_dict.copy()
    #     log_user_dict.pop("pw_hash", None)
    #
    #     log_payload = {
    #         "timestamp": datetime.now(timezone.utc),
    #         "user_id": editor_id,
    #         "username": editor_username,
    #         "target_id": new_user_doc["_id"],
    #         "target_name": new_user_doc["username"],
    #         "task": task,
    #         "edit": log_user_dict
    #     }
    #     print(f"{log_payload=}")
    #     cls.update_log(log_payload)
    #
    #     return User.build(new_user_doc)

    @classmethod
    def lookup_user(cls, attr, value):
        cls.connect()
        user_doc = cls.__users.find_one({attr: value})
        if user_doc:
            return User.build(user_doc)
        else:
            return None





    @classmethod
    def save_branch(cls, branch_dict, branch_map):
        """ This either saves or creates a new branch. """
        cls.connect()

        # I receive a dict with either no id and the dict to create or an existing id and edits.
        # or an id and a disable/enable request
        branch = False
        query_filter = {}
        task = ""
        if branch_dict.get("_id", False):
            branch_id = branch_dict["_id"]
            query_filter["_id"] = branch_id
            branch_dict.pop("_id")
            if "is_active" in branch_dict:
                if branch_dict["is_active"] is True:
                    task = "Enable Branch"
                elif branch_dict["is_active"] is False:
                    task = "Disable Branch"
            else:
                task = "Edit Branch"
            branch = TreeEngine.lookup_branch(branch_id)
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
            "edit": {
                "after": branch_dict,
                "before": {}
            }
        }
        if branch:
            for edit in branch_dict:
                log_payload["edit"]["before"][edit] = (getattr(branch, edit))

        # print(f"{log_payload=}")
        cls.update_log(log_payload)

        return Branch.build(new_branch_doc, branch_map)


    # @classmethod
    # def disable_branch(cls, branch):
    #     cls.connect()
    #     disabled_branch = cls.__branches.update_one(
    #         {"_id": branch.id},
    #         {"$set": {"is_active": False}}
    #     )
    #
    #     if disabled_branch:
    #         print("Disabled branch")
    #         log_payload = {
    #             "timestamp": datetime.now(timezone.utc),
    #             "user_id": current_user.id,
    #             "username": current_user.username,
    #             "target_id": branch.id,
    #             "target_name": branch.name,
    #             "task": "Disable Branch",
    #             "edit": {
    #                 "before": {"is_active": True},
    #                 "after": {"is_active": False}
    #             }
    #         }
    #         cls.update_log(log_payload)
    #         branch.is_active = False  # update local Object
    #     else:
    #         print("Did not disable branch.")

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
        query_filter = {}
        task = ""
        leaf = False

        if leaf_dict.get("_id", False):
            leaf_id = leaf_dict["_id"]
            query_filter["_id"] = leaf_id
            leaf_dict.pop("_id")
            if "is_active" in leaf_dict:
                if leaf_dict["is_active"] is True:
                    task = "Enable Leaf"
                elif leaf_dict["is_active"] is False:
                    task = "Disable Leaf"
            else:
                task = "Edit Leaf"
            leaf = TreeEngine.lookup_leaf(leaf_id)

        else:
            query_filter["_id"] = ObjectId()
            task = "Create Leaf"


        # Replaces everything else.
        update_payload = {
            "$set": leaf_dict
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
            "task": task,
            "edit": {"before": {},
                     "after": leaf_dict}
        }
        if leaf:
            for edit in leaf_dict:
                log_payload["edit"]["before"][edit] = (getattr(leaf, edit))

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
    def disable_leaf(cls, leaf): # FIXME can be simplified with branch/leaf
        cls.connect()
        disabled_leaf = cls.__leaves.update_one(
            {"_id": leaf.id},
            {"$set": {"is_active": False}}
        )

        if disabled_leaf:
            print("Disabled leaf")
            log_payload = {
                "timestamp": datetime.now(timezone.utc),
                "user_id": current_user.id,
                "username": current_user.username,
                "target_id": leaf.id,
                "target_name": leaf.subcategory,
                "task": "Disable Leaf",
                "edit": {
                    "before": {"is_active": True},
                    "after": {"is_active": False}
                }
            }
            cls.update_log(log_payload)
        else:
            print("Did not disable leaf.")

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
    def update_class(cls, class_db, property_dict):
        """ Used when needing to add property to an entire class """
        cls.connect()

        for prop, default_value in property_dict.items():
            class_db.update_many(
                {
                    "$or": [
                        {prop: {"$exists": False}},
                        {prop: None},
                        {prop: ""}
                    ]
                },
                {"$set": {prop: default_value}}

            )

    @classmethod
    def add_authorship(cls):
        """ Used to ensure all objects had author. """
        cls.connect()
        user = UserManager.lookup_user_name("josh")
        user_id = user.id
        property_dict = {"author_id": user_id}

        cls.update_class(cls.__leaves, property_dict)
        cls.update_class(cls.__branches, property_dict)

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
