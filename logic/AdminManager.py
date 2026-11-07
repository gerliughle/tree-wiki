from functools import wraps
from flask import abort
from flask_login import current_user

import math

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

    @staticmethod
    def paginate(data_list, page_number, per_page):
        print(f"{len(data_list)=}")


        slice_end = page_number * per_page
        slice_start = slice_end - per_page
        data_list_slice = data_list[slice_start:slice_end]
        print(f"{len(data_list_slice)=}")
        print(f"{slice_end=} {slice_start=}")
        total_pages = math.ceil(len(data_list) / per_page)
        print(f"{total_pages=}")

        return data_list_slice, {
            "page_number": page_number,
            "slice_start": slice_start,
            "slice_end": slice_end,
            "total_pages": total_pages,
        }
