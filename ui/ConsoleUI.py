from logic.Branch import Branch
from logic.Leaf import Leaf

class ConsoleUI:
    all_branches = []
    all_leaves = []

    @classmethod
    def init(cls):
        """ Generate the branch and leaf objects. """
        cls.all_branches, cls.all_leaves = Branch.read_data()

    @classmethod
    def run(cls):
        for branch in cls.all_branches:
            print(branch.name)


if __name__ == "__main__":
    ConsoleUI.init()
    ConsoleUI.run()