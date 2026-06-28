from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from flask import render_template, request, session
from flask_login import current_user, login_required
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
        branch_image = ""
        if "branch_name" in request.form:
            branch_name = request.form["branch_name"].strip()
            branch_image = str(branch_name.strip().lower().replace(" ", "_") + ".jpg")
        if "branch_description" in request.form:
            branch_description = request.form["branch_description"].strip()
        if "parent_branch_id" in request.form:
            parent_branch_id = ObjectId(request.form["parent_branch_id"])
        else:
            print("No branch id")
        branch_author = session.get("user_id")
        if branch_name == "" or branch_description == "" or parent_branch_id == "":
            return render_template("error.html")
        branch_dict = {
            "author_id": branch_author,
            "name": branch_name,
            "description": branch_description,
            "image": branch_image,
            "parent_id": parent_branch_id
        }
        branch = TreeEngine.add_branch(branch_dict)
        return render_template("edit/confirm_branch_created.html", branch=branch)

    @staticmethod
    @__app.route('/select_edit_branch')
    def select_edit_branch():
        all_branches = WebUI.get_all_branches()
        return render_template("edit/select_edit_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/edit_branch', methods=['POST'])
    def edit_branch():
        all_branches = WebUI.get_all_branches()
        branch_id = ""
        if "branch_id" in request.form:
            branch_id = ObjectId(request.form["branch_id"])
        print(f"{branch_id=}")
        branch = TreeEngine.lookup_branch(branch_id)
        print(f"Branch loaded if this is a name: {branch.name}")
        return render_template("edit/edit_branch.html", edit_branch=branch, branches=all_branches)

    @staticmethod
    @__app.route('/do_edit_branch', methods=['POST'])
    def do_edit_branch():
        """ FIXME needs lots of form validation, checking dupes, etc.


        Note for tomorrow josh: you are modifying this to edit a branch.
        this is a UI layer, you want to pass an 'update' dict to the tree engine
        which passes to database to update_one.

        the update_one thing takes the id to update, then $set: payload. """
        branch_id = ObjectId(request.form["branch_id"])
        branch_edits = {}
        if "branch_name" in request.form:
            if request.form["branch_name"].strip() != "":
                name = request.form["branch_name"].strip()
                branch_edits["name"] = name
                branch_edits["image"] = str(name.strip().lower().replace(" ", "_") + ".jpg")
        if "branch_description" in request.form:
            if request.form["branch_description"].strip() != "":
                branch_edits["description"] = request.form["branch_description"].strip()
        if "parent_branch_id" in request.form:
            if request.form["parent_branch_id"] != "":
                branch_edits["parent_id"] = ObjectId(request.form["parent_branch_id"])

        branch_author = session.get("user_id")
        print(f"Testing flask_login. {branch_author=}")
        updated_branch = TreeEngine.edit_branch(branch_id, branch_edits)
        return render_template("edit/confirm_branch_updated.html", branch=updated_branch)
