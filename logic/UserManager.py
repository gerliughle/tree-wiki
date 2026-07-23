from bson import ObjectId
from functools import wraps

from flask import render_template, abort
from flask_login import current_user

class UserManager:


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
