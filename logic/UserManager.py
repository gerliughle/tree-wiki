from bson import ObjectId
from functools import wraps
from flask import abort
import requests
from flask_login import current_user
import os
from configparser import ConfigParser

from logic.Validate import Validate


class UserManager:
    APP_NAME = "bonsaitree"
    __all_users = []

    @classmethod
    def __init__(cls):
        from data.Database import Database
        cls.__all_users = Database.read_users()
        print(f"Users loaded: {len(cls.__all_users)}")

    @staticmethod
    def role_required(*roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return abort(401)
                if current_user.role not in roles:
                    return abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @staticmethod
    def lookup_user_id(user_id):
        """ Takes id as str, then passes to db to look up. """
        from data.Database import Database
        user_id = Validate.validate_objectid(user_id)
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

    @classmethod
    def get_users(cls):
        return cls.__all_users

    @classmethod
    def save_user(cls, user_dict, save_type):
        from data.Database import Database
        print("UserManager - Saving User")
        user = Database.db_save(user_dict, save_type, "user")
        cls.__all_users = Database.read_users()
        return user

    @classmethod
    def delete_user(cls, user_id):
        from data.Database import Database
        user_id = Validate.validate_objectid(user_id)
        delete_user = cls.lookup_user_id(ObjectId(user_id))
        Database.delete_user(delete_user)
        cls.__all_users = Database.read_users()

    @classmethod
    def verify_turnstile(cls, token, remote_ip):
        """ Verifies Cloudflare turnstile token to mitigate bot requests. """

        home_path = os.environ['HOME']
        path = os.path.join(home_path, cls.APP_NAME)
        file = os.path.join(path, f"{cls.APP_NAME}.ini")
        if not os.path.exists(file):
            raise FileNotFoundError(f'{file} not found.')

        config_parser = ConfigParser()
        config_parser.read(file)
        turnstile_secret_key = config_parser.get("Turnstile", "turnstile_secret_key")

        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": turnstile_secret_key,
                "response": token,
                "remoteip": remote_ip
            },
            timeout=5
        )
        result = response.json()
        return result.get("success", False)
