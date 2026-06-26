from ui.WebUI import WebUI
from flask import render_template


# Routes needed:
# Admin routes:
# - Create Branch
# - Edit Branch
# - Create Leaf
# - Edit Leaf
# - Duplicate leaf to new branch

# User routes:
# - Provide suggestion on branch
# - Provide suggestion on leaf

# Also need to implement where this is on site. Admins have an edit page in menu?
# Suggestion button somewhere



class EditRoutes(WebUI):
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/create_branch')
    def create_branch():
        return render_template("edit/create_branch.html")
