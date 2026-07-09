from flask import session, g
from flask_login import LoginManager
from logic.User import User
from bson import ObjectId

class UserManager:
    # __all_users = []

    @staticmethod
    def lookup_user_id(user_id):
        """ Takes id as str, then passes to db to look up. """
        from data.Database import Database
        user_id = ObjectId(user_id)
        user = Database.lookup_user("_id", user_id)
        if user:
            return user
        else:
            return None

    @classmethod
    def lookup_user_name(cls, username):
        """Login verification lookup."""
        from data.Database import Database
        user = Database.lookup_user("username", username)
        if user:
            return user
        else:
            return None
    # @classmethod
    # def read_user(cls, username):
    #     for user in cls.all_users:
    #         if username == user.username:
    #             print("Username match.")
    #             return user
    #     else:
    #         print("No username match.")
    #         return None

    # @classmethod
    # def __init__(cls):
    #     from data.Database import Database
    #     cls.all_users = Database.read_users()
    #     print(f"Users loaded: {len(cls.all_users)}")

    # @classmethod
    # def get_all_users(cls):
    #     return cls.all_users

    # @classmethod
    # def login(cls, user):
    #     session["user_id"] = str(user.id)
    #
    # @staticmethod
    # def logout():
    #     session.pop("user_id", None)

    # @classmethod
    # def add_user(cls, username, pw_hash):
    #     from data.Database import Database
    #     user = Database.add_user(username, pw_hash)
    #     cls.all_users.append(user)
    #     return user