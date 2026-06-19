from logic.Branch import Branch
from logic.TreeEngine import TreeEngine

class ConsoleUI:
    engine = None
    category_list = []

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()

    @classmethod
    def run(cls):

        branch_name = "Japanese Maple"

        #WHAT IS MY TESTING GOAL?
        # I want an engine file to work.
        # In console ui, I want to be able to send in a branch name, and get its id
        # I dont even know if this is useful but helpful to learn the system
        #then, search the name, and return any leaf it has as a parent
        print("\nTesting branch lookup:")

        branch = cls.engine.lookup_branch_by_name(branch_name)

        if branch:
            print(f"{branch.name=}")
            print(f"{branch._id=}")
        print()


        #Goal 2:
        # show the number of leaves that a branch has.
        leaves = TreeEngine.get_leaves_for_branch(branch._id)
        print(f"Number of leaves for {branch.name}: {len(leaves)}")
        print()

        # goal 3: update category list
        every_leaf = TreeEngine.get_leaves()

        for leaf in every_leaf:
            if leaf.category not in cls.category_list:
                cls.category_list.append(leaf.category)

        #goal 4
        # create a very simple layout
        leaves = TreeEngine.get_care_guide(branch._id)

        print(f"# of leaves in inherited care guide: {len(leaves)}\n\n")
        cls.display_care_guide(branch, leaves)

        #goal 5
        # Incorporate filters.



    @classmethod
    def display_care_guide(cls, branch, leaves):
        """ Present a branch care guide. """

        print(f"~~~{branch.name}~~~")
        print(branch.description)

        for category in cls.category_list:
            check = True


            for leaf in leaves:
                if len(leaf.phases) + len(leaf.seasons) == 0:
                    continue # Skips no/no leaves.
                if leaf.category == category:
                    if check:
                        print(f"\nCategory: {category}")
                        check = False
                    print(f"   Subcategory: {leaf.subcategory}")
                    print(f"   Source: {TreeEngine.lookup_branch(leaf.branch_id).name}")
                    print(f"   Seasons:{leaf.seasons}")
                    print(f"   Phases: {leaf.phases}")
                    print(f"   {leaf.text}\n")








if __name__ == "__main__":
    ConsoleUI.init()
    ConsoleUI.run()