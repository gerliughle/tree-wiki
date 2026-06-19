
class Branch:

    def __init__(self,
                 _id,
                 author_id,
                 name,
                 branch_map):
        self._id = _id
        self.author_id = author_id
        self.name = name
        branch_map[_id] = self

    @classmethod
    def build(cls, branch_dict, branch_map):
        """ Build a branch, add to map. """
        return Branch(
            branch_dict['_id'],
            branch_dict['author_id'],
            branch_dict['name'],
            branch_map
        )

    @staticmethod
    def read_data():
        """ Return the objects from the database. """
        from data.Database import Database
        return Database.read_data()


    @classmethod
    def lookup_branch_id(cls, _id):
        """ Return the Branch object for _id """
        return cls.branch_map[_id]

    @staticmethod
    def get_leaves_for_branch(branch_id):
        pass


    def __str__(self):
        return f"Branch object: {self.name}. Id: {self._id}"