from logic.Branch import Branch
from logic.TreeEngine import TreeEngine

class ConsoleUI:
    engine = None
    category_list = []

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()
        print("ClassUI initialized.")
        print("Engine created.")

    @classmethod
    def run(cls):

        print("Running program.")

        branch_name = "Japanese Maple"

        #WHAT IS MY TESTING GOAL?
        # I want an engine file to work.
        # In console ui, I want to be able to send in a branch name, and get its id
        # I dont even know if this is useful but helpful to learn the system
        #then, search the name, and return any leaf it has as a parent
        print("Testing branch lookup:")

        branch = cls.engine.lookup_branch_by_name(branch_name)

        if branch:
            print(f"{branch.name=}")
            print(f"{branch._id=}")


        #Goal 2:
        # show the number of leaves that a branch has.

        leaves = TreeEngine.get_leaves_for_branch(branch._id)


        print(f"Number of leaves for {branch.name}: {len(leaves)}")


        #goal 3
        # create a very simple layout
        cls.display_care_guide(branch)

        #goal 4: update category list
        every_leaf = TreeEngine.get_leaves()
        for leaf in every_leaf:
            if leaf.category not in cls.category_list:
                cls.category_list.append(leaf.category)
        print(cls.category_list)

    @classmethod
    def display_care_guide(cls, branch):
        """ Present a branch care guide. """

        leaves = TreeEngine.get_leaves_for_branch(branch._id, cls.engine.db)

        print(branch.name)
        print("A simple care guide.\n")

        current_category = None
        for leaf in leaves:
            if leaf.category == current_category:
                pass








if __name__ == "__main__":
    ConsoleUI.init()
    ConsoleUI.run()