
class Leaf:
    def __init__(self,
                 _id,
                 author_id,
                 branch_id,
                 category,
                 subcategory,
                 seasons,
                 entries,
                 leaf_map):
        self._id = _id
        self.author_id = author_id
        self.branch_id = branch_id
        self.category = category
        self.subcategory = subcategory
        self.seasons = seasons
        self.entries = entries
        leaf_map[_id] = self

    @classmethod
    def build(cls, leaf_dict, leaf_map):
        """ Builds object from dict and adds to map. """
        return Leaf(
            leaf_dict["_id"],
            leaf_dict["author_id"],
            leaf_dict["branch_id"],
            leaf_dict["category"],
            leaf_dict["subcategory"],
            leaf_dict["seasons"],
            leaf_dict["entries"],
            leaf_map
        )

    def to_dict(self):
        return {
            "_id": self._id,
            "author_id": self.author_id,
            "branch_id": self.branch_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "seasons": self.seasons,
            "entries": self.entries
        }

    @property
    def id(self):
        return self._id

