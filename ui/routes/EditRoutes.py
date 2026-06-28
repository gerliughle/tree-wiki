from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from flask import render_template, request, session
from bson import ObjectId


# Routes needed:
# Admin routes:
# - Create Branch - yeehaw.
# - Edit Branch. Can make a form that pulls name/desc as defaults, lets you change.
# - delete branch
# - Create Leaf
# - Edit Leaf
# - Duplicate leaf to new branch

# User routes:
# - Provide suggestion on branch
# - Provide suggestion on leaf

# Also need to implement where this is on site. Admins have an edit page in menu?
# Suggestion button somewhere


class EditRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/create_branch')
    def create_branch():
        all_branches = WebUI.get_all_branches()
        return render_template("edit/create_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/do_create_branch', methods=['POST'])
    def do_create_branch():
        """ FIXME needs lots of form validation, checking dupes, etc. """
        branch_name = ""
        branch_description = ""
        parent_branch_id = ""
        if "branch_name" in request.form:
            branch_name = request.form["branch_name"].strip()
        if "branch_description" in request.form:
            branch_description = request.form["branch_description"].strip()
        if "parent_branch_id" in request.form:
            parent_branch_id = request.form["parent_branch_id"]
        else:
            print("No branch id")
        branch_image = str(branch_name.strip().lower().replace(" ", "_") + ".jpg")
        branch_author = session.get("user_id")
        print(f"{parent_branch_id=}")

        # user = UserManager.add_user(username, pw_hash)

        # call a logic, pass the params.
        branch_dict = {
            "author_id": branch_author,
            "name": branch_name,
            "description": branch_description,
            "image": branch_image,
            "parent_id": ObjectId(parent_branch_id)
        }
        TreeEngine.add_branch(branch_dict)

        return render_template("edit/confirm_branch_created.html")
