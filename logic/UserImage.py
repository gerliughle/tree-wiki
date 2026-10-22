from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager

class UserImage:

    def __init__(self,
                 _id,
                 is_active,
                 author_id,
                 branch_id,
                 ext,
                 is_approved, # Bool. If false, needs to either be set to inactive, or approved.
                 quality,
                 caption,
                 image_map):
        self._id = _id
        self.is_active = is_active
        self.author_id = author_id
        self.branch_id = branch_id
        self.ext = ext
        self.is_approved = is_approved
        self.quality = quality
        self.caption = caption
        image_map[_id] = self

    @classmethod
    def build(cls, img_dict, image_map):
        """ Builds object from dict and adds to map. """
        return UserImage(
            img_dict["_id"],
            img_dict["is_active"],
            img_dict["author_id"],
            img_dict["branch_id"],
            img_dict["ext"],
            img_dict["is_approved"],
            img_dict["quality"],
            img_dict.get("caption", None),
            image_map
        )

    def to_dict(self):
        return {
            "_id": self._id,
            "is_active": self.is_active,
            "author_id": self.author_id,
            "branch_id": self.branch_id,
            "ext": self.ext,
            "approved": self.is_approved,
            "quality": self.quality,
            "caption": self.caption,
        }

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        branch_name = TreeEngine.lookup_branch(self.branch_id).name
        author_name = UserManager.lookup_user_id(self.author_id).name
        return str(f"'{branch_name}' Image by {author_name}")

    @property
    def branch_name(self):
        return TreeEngine.lookup_branch(self.branch_id).name

    @property
    def author_username(self):
        return UserManager.lookup_user_id(self.author_id).username