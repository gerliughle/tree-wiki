from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from flask import render_template, request, session, redirect, url_for
from flask_login import current_user, login_required
from bson import ObjectId


# Routes needed:
# Admin routes:
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
        branch = TreeEngine.save_branch(branch_dict)
        return render_template("edit/confirm_branch_created.html", branch=branch)



    # FIXME URGENT: There is something borked. I think it's editing the wrong branch, and maybe
    # mixing the parent branch with the edit branch.
    # Trace the branch id's that are passed.
    @staticmethod
    @__app.route('/select_edit_branch')
    def select_edit_branch():
        all_branches = WebUI.get_all_branches()
        return render_template("edit/select_edit_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/edit_branch', methods=['POST'])
    def edit_branch():
        all_branches = WebUI.get_all_branches()
        branch_id = ObjectId(request.form["select_branch_id"])
        print(f"{branch_id=}")
        branch = TreeEngine.lookup_branch(branch_id)
        print(f"Branch loaded if this is a name: {branch.name}")
        return render_template("edit/edit_branch.html", edit_branch=branch, branches=all_branches)

    @staticmethod
    @__app.route('/do_edit_branch', methods=['POST'])
    def do_edit_branch():
        """ FIXME needs lots of form validation, checking dupes, etc.

        Form design should have better labels, and be better in general. """
        branch_id = ObjectId(request.form["branch_id"])
        branch_edits = {"_id": branch_id}
        if "branch_name" in request.form:
            if request.form["branch_name"].strip() != "":
                name = request.form["branch_name"].strip()
                branch_edits["name"] = name
                branch_edits["image"] = str(name.strip().lower().replace(" ", "_") + ".jpg")
        if "branch_description" in request.form:
            if request.form["branch_description"].strip() != "":
                branch_edits["description"] = request.form["branch_description"].strip()
        if "select_branch_id" in request.form:
            if request.form["select_branch_id"] != "":
                branch_edits["parent_id"] = ObjectId(request.form["select_branch_id"])

        branch_author = session.get("user_id")
        print(f"Testing flask_login. {branch_author=}")
        updated_branch = TreeEngine.save_branch(branch_edits)
        return render_template("edit/confirm_branch_updated.html", branch=updated_branch)

    @staticmethod
    @__app.route('/select_delete_branch')
    def delete_branch():
        all_branches = WebUI.get_all_branches()
        return render_template("edit/select_delete_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/check_delete_branch', methods=['POST'])
    def check_delete_branch():
        delete_branch = ""
        if "select_branch_id" in request.form:
            delete_branch = TreeEngine.lookup_branch(ObjectId(request.form["select_branch_id"]))
        print(f"Delete branch name: {delete_branch.name=}")
        return render_template("edit/check_delete_branch.html", delete_branch=delete_branch)

    @staticmethod
    @__app.route('/do_delete_branch', methods=['POST'])
    def do_delete_branch():
        delete_name = ""
        if "branch_id" in request.form:
            delete_branch_id = ObjectId(request.form["branch_id"])
            delete_name = TreeEngine.delete_branch(delete_branch_id)
        return render_template("edit/confirm_branch_deleted.html", delete_name=delete_name)

    @staticmethod
    @__app.route('/select_edit_leaf')
    def select_edit_leaf():
        all_branches = WebUI.get_all_branches()
        return render_template("edit/select_edit_leaf.html", all_branches=all_branches)

    @staticmethod
    @__app.route('/leaf_editor', methods=['POST'])
    def leaf_editor():
        branch_id = ""
        if "select_branch_id" in request.form:
            branch_id = ObjectId(request.form["select_branch_id"])

        branch = TreeEngine.lookup_branch(branch_id)
        branch_leaves = TreeEngine.get_leaves_for_branch(branch_id)
        inherited_leaves = TreeEngine.get_inherited_leaves(branch_id)
        print(f"Branch_leaves count: {len(branch_leaves)}. Inherited_leaves count: {len(inherited_leaves)}")

        page_context = {
            "branch":branch,
            "branch_leaves":branch_leaves,
            "inherited_leaves":inherited_leaves
        }
        return render_template('edit/leaf_editor.html', **page_context)


    @staticmethod
    @__app.route('/edit_leaf', methods=['POST'])
    def edit_leaf():
        leaf_id = "" # The branch i am cloning from
        target_branch_id = "" # The branch i am creating a leaf for


        if "target_branch_id" in request.form:
            target_branch_id = ObjectId(request.form["target_branch_id"])
        target_branch = TreeEngine.lookup_branch(target_branch_id)

        if "leaf_id" in request.form:
            leaf_id = ObjectId(request.form["leaf_id"])
        leaf = TreeEngine.lookup_leaf(leaf_id)
        source_branch_id = leaf.branch_id
        source_branch = TreeEngine.lookup_branch(source_branch_id)
        print(f"{source_branch=}, {target_branch=}")
        if source_branch.id == target_branch.id:
            print("Source and target match")

        return render_template("edit/edit_leaf.html", leaf=leaf, source_branch=source_branch, target_branch=target_branch)

    @staticmethod
    @__app.route('/do_edit_leaf', methods=['POST'])
    def do_edit_leaf():
        """ FIXME more validation """
        branch_id = ""
        category = ""
        subcategory = ""

        if "branch_id" in request.form:
            branch_id = ObjectId(request.form["branch_id"])
        if "category" in request.form:
            category = request.form["category"]
        if "subcategory" in request.form:
            subcategory = request.form["subcategory"]
        author_id = session.get("user_id") # Eventually, a more robust editor tracking system could be used. Now, last editor rewrites creator.
        season_list = ['Spring', 'Summer', 'Fall', 'Winter']
        seasons = []
        for season in season_list:
            if season in request.form:
                seasons.append(season)
        entries = []
        for i in range(1,5):
            if 'entry_enabled_'+str(i) in request.form:
                phases = []
                if 'phase_1st_' + str(i) in request.form:
                    phases.append("1st")
                if 'phase_2nd_' + str(i) in request.form:
                    phases.append("2nd")
                if 'phase_3rd+_' + str(i) in request.form:
                    phases.append("3rd+")
                entry = {"text": request.form["entry_text_" + str(i)], "phases": phases}
                entries.append(entry)
        leaf_dict = {
            "author_id": author_id,
            "branch_id": branch_id,
            "category": category,
            "subcategory": subcategory,
            "seasons": seasons,
            "entries": entries
        }
        leaf = TreeEngine.save_leaf(leaf_dict)
        if leaf:
            print(f"leaf created. Id: {leaf.id}")
        else:
            print(f"No leaf created and returned.")
        branch = TreeEngine.lookup_branch(branch_id)
        return render_template("edit/confirm_leaf_created.html", leaf=leaf, branch=branch)


    @staticmethod
    @__app.route('/check_delete_leaf', methods=['POST'])
    def check_delete_leaf():
        delete_leaf = ""
        if "delete_leaf_id" in request.form:
            delete_leaf = TreeEngine.lookup_leaf(ObjectId(request.form["delete_leaf_id"]))
        if delete_leaf:
            print("Delete leaf selected")
        else:
            print("No leaf found to delete.")
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        return render_template("edit/check_delete_leaf.html", delete_leaf=delete_leaf, branch=branch)

    @staticmethod
    @__app.route('/do_delete_leaf', methods=['POST'])
    def do_delete_leaf():
        delete_leaf_id = ""
        if "leaf_id" in request.form:
            delete_leaf_id = ObjectId(request.form["leaf_id"])
        delete_leaf = TreeEngine.lookup_leaf(delete_leaf_id)
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        TreeEngine.delete_leaf(delete_leaf_id)

        return render_template("edit/confirm_leaf_deleted.html", branch=branch)