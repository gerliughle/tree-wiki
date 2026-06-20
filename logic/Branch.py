
class Branch:

    def __init__(self,
                 _id,
                 author_id,
                 name,
                 description,
                 parent_id,
                 branch_map):
        self._id = _id
        self.author_id = author_id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        branch_map[_id] = self

    @classmethod
    def build(cls, branch_dict, branch_map):
        """ Build a branch, add to map. """
        return Branch(
            branch_dict["_id"],
            branch_dict['author_id'],
            branch_dict['name'],
            branch_dict['description'],
            branch_dict['parent_id'],
            branch_map
        )

    def to_dict(self):
        return {
            '_id': self._id,
            'author_id': self.author_id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id
        }

    @staticmethod
    def get_leaves_for_branch(branch_id):
        pass


    def __str__(self):
        return f"Branch object: {self.name}. Id: {self._id}"