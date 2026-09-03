from bson import ObjectId
from functools import wraps
from flask import abort
import requests
from flask_login import current_user
from profanity_check import predict
from wordsegment import load, segment
from better_profanity import profanity
import os
from configparser import ConfigParser

class UserManager:
    APP_NAME = "bonsaitree"
    __all_users = []
    load()
    profanity.load_censor_words()

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
        delete_user = cls.lookup_user_id(ObjectId(user_id))
        Database.delete_user(delete_user)
        cls.__all_users = Database.read_users()

    @staticmethod
    def normalize_text(text):
        text = text.lower()
        char_map = {
            '@': 'a',
            '4': 'a',
            '0': 'o',
            '1': 'i',
            '!': 'i',
            '3': 'e',
            '$': 's',
            '5': 's',
            '7': 't'
        }
        for char, replacement in char_map.items():
            text = text.replace(char, replacement)
        return text

    @staticmethod
    def is_username_profane(username):
        """ Cleans, segments and then uses two profanity detectors to try and limit offensive usernames.
        This isn't as big of a deal as comments because right now, I don't think these names are visible
        to other users, but authorship could be bigger later. """

        username_clean = UserManager.normalize_text(username)
        words = segment(username_clean)
        segmented_username = " ".join(words)
        profane_word = profanity.contains_profanity(segmented_username)
        profane_text = predict([segmented_username])
        print(segmented_username)
        print(profane_word, profane_text)
        if profane_word or profane_text:
            return True
        else:
            return False

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
