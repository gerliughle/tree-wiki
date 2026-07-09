from bson import ObjectId

class UserManager:

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
