from ui.WebUI import WebUI
from logic.TreeEngine import TreeEngine
from logic.UserManager import UserManager
from logic.AdminManager import AdminManager
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from bson import ObjectId


class EditRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @login_required
    @UserManager.role_required("admin", "editor")
    @__app.route('/create_branch', methods=['POST'])
    def create_branch():
        branch = None
        all_branches = TreeEngine.get_branches()
        branch_id = request.form.get("select_branch_id")
        if branch_id:
            branch = TreeEngine.lookup_branch(ObjectId(branch_id))

        return render_template("edit/create_branch.html", branches=all_branches, branch=branch)

    @staticmethod
    @__app.route('/do_create_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
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
        branch_author = current_user.id
        if branch_name == "" or branch_description == "" or parent_branch_id == "":
            return render_template("error.html")
        branch_dict = {
            "author_id": branch_author,
            "is_active": True,
            "name": branch_name,
            "description": branch_description,
            "image": branch_image,
            "parent_id": parent_branch_id
        }
        branch = TreeEngine.save_branch(branch_dict, "create")
        return render_template("edit/confirm_branch_created.html", branch=branch)

    @staticmethod
    @__app.route('/select_edit_branch')
    @login_required
    @UserManager.role_required("admin", "editor")
    def select_edit_branch():
        all_branches = TreeEngine.get_branches()
        return render_template("edit/select_edit_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/edit_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_branch():
        all_branches = TreeEngine.get_branches()
        branch_id = ObjectId(request.form["select_branch_id"])
        print(f"{branch_id=}")
        branch = TreeEngine.lookup_branch(branch_id)
        print(f"Branch loaded if this is a name: {branch.name}")
        return render_template("edit/edit_branch.html", edit_branch=branch, branches=all_branches)

    @staticmethod
    @__app.route('/do_edit_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
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

        branch_author = current_user.id
        branch_edits["author_id"] = branch_author
        updated_branch = TreeEngine.save_branch(branch_edits, "edit")
        return render_template("edit/confirm_branch_updated.html", branch=updated_branch)

    @staticmethod
    @__app.route('/select_delete_branch')
    @login_required
    @UserManager.role_required("admin")
    def delete_branch():
        all_branches = TreeEngine.get_branches()
        return render_template("edit/select_delete_branch.html", branches=all_branches)

    @staticmethod
    @__app.route('/check_delete_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_branch():
        delete_branch = ""
        if "select_branch_id" in request.form:
            delete_branch = TreeEngine.lookup_branch(ObjectId(request.form["select_branch_id"]))
        print(f"Delete branch name: {delete_branch.name=}")
        return render_template("edit/check_delete_branch.html", delete_branch=delete_branch)

    @staticmethod
    @__app.route('/do_delete_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_branch():
        delete_name = ""
        if "branch_id" in request.form:
            delete_branch_id = ObjectId(request.form["branch_id"])
            delete_name = TreeEngine.delete_branch(delete_branch_id)
        return render_template("edit/confirm_branch_deleted.html", delete_name=delete_name)

    @staticmethod
    @__app.route('/check_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_branch():
        disable_branch = ""
        if "select_branch_id" in request.form:
            disable_branch = TreeEngine.lookup_branch(ObjectId(request.form["select_branch_id"]))
        print(f"Disable branch name: {disable_branch.name=}")
        return render_template("edit/check_disable_branch.html", disable_branch=disable_branch)

    @staticmethod
    @__app.route('/do_disable_branch', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_branch():
        if "branch_id" in request.form:
            disable_branch_id = ObjectId(request.form["branch_id"])
            branch_dict = {"_id": disable_branch_id,
                           "is_active": False}
            disable_branch = TreeEngine.save_branch(branch_dict, "disable")
        return render_template("edit/confirm_branch_disabled.html", disable_branch=disable_branch)

    @staticmethod
    @__app.route('/select_edit_leaf')
    @login_required
    @UserManager.role_required("admin", "editor")
    def select_edit_leaf():
        all_branches = TreeEngine.get_branches()
        return render_template("edit/select_edit_leaf.html", all_branches=all_branches)

    @staticmethod
    @__app.route('/select_edit_leaf_type', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def select_edit_leaf_type():
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
            "inherited_leaves":inherited_leaves,
            "all_categories": TreeEngine.CATEGORIES
        }
        return render_template('edit/select_edit_leaf_type.html', **page_context)

    @staticmethod
    @__app.route('/edit_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def edit_leaf():
        """ Leaf editing router

        Either clone, edit, or create new.
        leaf: clone source, edit source, or None
        source_branch: branch the leaf is sourced from, or being edited, or None.
        target_branch: branch_id for this leaf. this is selected in step 1. if this matches source, you're editing
        category_name: if creating a new subcat, this will exist. there will be no leaf_id or source branch.
        """

        leaf = None # The branch i am cloning from
        target_branch = None # The branch i am creating a leaf for
        source_branch = None
        category_name = None

        if "target_branch_id" in request.form:
            target_branch_id = ObjectId(request.form["target_branch_id"])
            target_branch = TreeEngine.lookup_branch(target_branch_id)

        if "leaf_id" in request.form:
            leaf_id = ObjectId(request.form["leaf_id"])
            leaf = TreeEngine.lookup_leaf(leaf_id)
            source_branch_id = leaf.branch_id
            source_branch = TreeEngine.lookup_branch(source_branch_id)

        if "category_name" in request.form:
            category_name = request.form["category_name"]

        return render_template("edit/edit_leaf.html", leaf=leaf, source_branch=source_branch, target_branch=target_branch, category_name=category_name)

    @staticmethod
    @__app.route('/do_edit_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_edit_leaf():
        """ FIXME more validation

        leaf_id is added if it is existing. Then in save_leaf, it uses that to determine different approach.
        It seems like this could be improved to only send changed data instead of all of it, but needs form update."""

        branch_id = ""
        category = ""
        subcategory = ""
        save_type = ""
        leaf_id = None

        if request.form.get("leaf_id"):
            leaf_id = ObjectId(request.form.get("leaf_id"))

        if "branch_id" in request.form:
            branch_id = ObjectId(request.form["branch_id"])
        if "category" in request.form:
            category = request.form["category"]
        if "subcategory" in request.form:
            subcategory = request.form["subcategory"]
        author_id = current_user.id # Eventually, a more robust editor tracking system could be used. Now, last editor rewrites creator.
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
            "is_active": True,
            "branch_id": branch_id,
            "category": category,
            "subcategory": subcategory,
            "seasons": seasons,
            "entries": entries
        }
        if leaf_id:
            leaf_dict["_id"] = leaf_id
            save_type = "edit"
        else:
            save_type = "create"
        leaf = TreeEngine.save_leaf(leaf_dict, save_type)
        if leaf:
            print(f"leaf created. Id: {leaf.id}")
        else:
            print(f"No leaf created and returned.")
        branch = TreeEngine.lookup_branch(branch_id)
        return render_template("edit/confirm_leaf_created.html", leaf=leaf, branch=branch)


    @staticmethod
    @__app.route('/check_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_leaf():
        delete_leaf = ""
        if "leaf_id" in request.form:
            delete_leaf = TreeEngine.lookup_leaf(ObjectId(request.form["leaf_id"]))
        if delete_leaf:
            print("Delete leaf selected")
        else:
            print("No leaf found to delete.")
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        return render_template("edit/check_delete_leaf.html", delete_leaf=delete_leaf, branch=branch)

    @staticmethod
    @__app.route('/do_delete_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_leaf():
        delete_leaf_id = ""
        if "leaf_id" in request.form:
            delete_leaf_id = ObjectId(request.form["leaf_id"])
        delete_leaf = TreeEngine.lookup_leaf(delete_leaf_id)
        branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
        TreeEngine.delete_leaf(delete_leaf_id)

        return render_template("edit/confirm_leaf_deleted.html", branch=branch)

    @staticmethod
    @__app.route('/check_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def check_disable_leaf():
        disable_leaf = ""
        if "leaf_id" in request.form:
            disable_leaf = TreeEngine.lookup_leaf(ObjectId(request.form["leaf_id"]))
        if disable_leaf:
            print("Disable leaf selected")
        else:
            print("No leaf found to delete.")
        branch = TreeEngine.lookup_branch(disable_leaf.branch_id)
        return render_template("edit/check_disable_leaf.html", disable_leaf=disable_leaf, branch=branch)

    @staticmethod
    @__app.route('/do_disable_leaf', methods=['POST'])
    @login_required
    @UserManager.role_required("admin", "editor")
    def do_disable_leaf():
        disable_leaf_id = ObjectId(request.form.get("leaf_id"))
        branch = TreeEngine.lookup_branch(TreeEngine.lookup_leaf(disable_leaf_id).branch_id)
        leaf_dict = {
            "_id": disable_leaf_id,
            "is_active": False
        }
        TreeEngine.save_leaf(leaf_dict, "disable")
        return render_template("edit/confirm_leaf_disabled.html", branch=branch)