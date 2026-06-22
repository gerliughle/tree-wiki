

class UserManager:
    __all_users = []

    @classmethod
    def __init__(cls):
        from data.Database import Database
        cls.all_users = Database.read_users()
        print(f"Users loaded: {len(cls.all_users)}")

    @classmethod
    def lookup_user(cls, user_id):
        for user in cls.all_users:
            if user.id == user_id:
                return user
        return None

    @classmethod
    def get_all_users(cls):
        return cls.all_users