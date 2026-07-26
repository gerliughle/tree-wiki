from bson import ObjectId
from functools import wraps
from flask import render_template, abort
from flask_login import current_user

class AdminManager:
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
    def get_audit_log():
        from data.Database import Database
        log = Database.get_audit_log()
        return log

    @staticmethod
    def get_audit_entry(log_id):
        from data.Database import Database
        log_entry = Database.get_audit_entry(log_id)
        return log_entry

