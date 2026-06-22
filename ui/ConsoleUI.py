from logic.Branch import Branch
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from logic.UserManager import UserManager

class ConsoleUI:
    engine = None
    category_list = []

    @classmethod
    def init(cls):
        cls.engine = TreeEngine()
        cls.usermanager = UserManager()

    @classmethod
    def run(cls):

        branch_name = "Japanese Maple"
        phase_filter=["1st", "2nd", "3rd+"]
        season_filter=["Spring"]

        #WHAT IS MY TESTING GOAL?
        # I want an engine file to work.
        # In console ui, I want to be able to send in a branch name, and get its id
        # I dont even know if this is useful but helpful to learn the system
        #then, search the name, and return any leaf it has as a parent
        print("\nTesting branch lookup:")

        branch = cls.engine.lookup_branch_by_name(branch_name)
        if branch is None:
            print(f"Error. No results for '{branch_name}'")

        #Goal 2:
        # show the number of leaves that a branch has.
        leaves = TreeEngine.get_leaves_for_branch(branch._id)
        print(f"Number of leaves for {branch.name}: {len(leaves)}")
        print()

        # goal 3: update category list.

        # build category list for grouping. Probably should be done manually for ordering.
        every_leaf = TreeEngine.get_leaves()

        for leaf in every_leaf:
            if leaf.category not in cls.category_list:
                cls.category_list.append(leaf.category)

        #goal 4
        # create a very simple layout
        inherited_leaves, heritage = TreeEngine.get_care_guide(branch._id)

        print(f"# of leaves in inherited care guide: {len(inherited_leaves)}\n\n")
        print("Heritage:")

        for branch in heritage:
            print(f"  {branch.name}")


        #goal 5
        # Incorporate filters.

        phase_filtered = TreeEngine.filter_phase(inherited_leaves, phase_filter)
        season_filtered = TreeEngine.filter_season(phase_filtered, season_filter)
        cls.display_care_guide(branch, season_filtered)

        all_users = cls.usermanager.get_all_users()
        user = all_users[0]
        print(f"Thank you, {user.username}.")


        #goal 6
        #print source list thing. too ez.


        #goal 7
        # actual database probably.
        # kinda done.
        # once this is sort of working, add user object, then add author to
        # so gotta figure out user stuff, and possibly userstate at same time.
        # all of everything i guess. login. right now, no real differenc, but knows who you are.
        # eventually can add in collections.

        # editing data.
        # taking a while to add in real data, thinking thru heirarchy,
        # then eventually starting a basic site with BOOTSTRAP




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