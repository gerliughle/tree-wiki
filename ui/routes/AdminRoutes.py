from ui.WebUI import WebUI
from logic.User import User
from logic.AdminManager import AdminManager
from logic.UserManager import UserManager
from logic.TreeEngine import TreeEngine

from flask import render_template, request, redirect, url_for
from flask_login import login_required
from bson import ObjectId


class AdminRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route('/log_action', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def log_action():
        """ Takes the action and log_id from admin dashboard buttons. Route to relevant next step. """

        save_type = ""

        log_id = request.form.get("log_id")
        action = request.form.get("action")
        log = AdminManager.get_audit_entry(ObjectId(log_id))
        target_id = ObjectId(log["target_id"])
        obj_type = log["obj_type"]
        obj_dict = {"_id": target_id}

        # Possible actions are log_disable, log_enable, log_revert, log_delete

        if action == "log_delete":
            print("Log Delete Selected")
            if obj_type == "Branch":
                delete_branch = TreeEngine.lookup_branch(ObjectId(target_id))
                return render_template("edit/check_delete_branch.html", delete_branch=delete_branch)
            elif obj_type == "Leaf":
                delete_leaf = TreeEngine.lookup_leaf(ObjectId(target_id))
                branch = TreeEngine.lookup_branch(delete_leaf.branch_id)
                return render_template("edit/check_delete_leaf.html", delete_leaf=delete_leaf, branch=branch)
            elif obj_type == "User":
                delete_user = UserManager.lookup_user_id(ObjectId(target_id))
                print(f"{delete_user=}")
                return render_template("admin/check_delete_user.html", user=delete_user)

        if action == "log_revert":
            print("Log Revert Selected")
            obj_dict = log["edit"]["before"]
            obj_dict["_id"] = target_id
            print(f"Debug {obj_dict=}")
            if obj_type == "Branch":
                TreeEngine.save_branch(obj_dict, "edit")
            elif obj_type == "Leaf":
                TreeEngine.save_leaf(obj_dict, "edit")
            elif obj_type == "User":
                UserManager.save_user(obj_dict, "edit")




        elif action == "log_enable":
            obj_dict["is_active"] = True
            save_type = "enable"
        elif action == "log_disable":
            obj_dict["is_active"] = False
            save_type = "disable"
        if action == "log_enable" or action == "log_disable":
            if obj_type == "User":
                UserManager.save_user(obj_dict, save_type)
            if obj_type == "Branch":
                TreeEngine.save_branch(obj_dict, save_type)
            if obj_type == "Leaf":
                TreeEngine.save_leaf(obj_dict, save_type)

        return redirect(url_for("admin_dashboard"))

    @staticmethod
    @__app.route("/manage_users")
    @login_required
    @UserManager.role_required("admin")
    def manage_users():
        users = UserManager.get_users()
        josh = UserManager.lookup_user_name("josh")
        if josh in users:
            users.remove(josh)
        return render_template("admin/manage_users.html", users=users)

    @staticmethod
    @__app.route("/edit_user", methods=["POST"])
    @login_required
    @UserManager.role_required("admin")
    def edit_user():
        username = request.form.get("user_selection")
        user = UserManager.lookup_user_name(username)
        if user and user.username != "josh":
            return render_template("admin/edit_user.html", user=user)
        else:
            print("User does not exist.")
            return redirect(url_for("do_login"))

    @staticmethod
    @__app.route("/do_edit_user", methods=["POST"])
    @login_required
    @UserManager.role_required("admin")
    def do_edit_user():
        save_type = ""
        new_pw_hash = ""

        user_id = request.form.get("user_id")
        user = UserManager.lookup_user_id(user_id)
        role_change = request.form.get("role_change")
        disable_account = request.form.get("disable_account")
        enable_account = request.form.get("enable_account")
        if request.form["password"] != "":
            new_pw_hash = User.hash_password(request.form["password"])

        if user and user.username != "josh":
            user_edits = {"_id": user.id}
            if role_change and role_change != "":
                user_edits["role"] = role_change
                save_type = "edit"
            elif new_pw_hash != "":
                user_edits["pw_hash"] = new_pw_hash
                save_type = "edit"
            elif disable_account:
                user_edits["is_active"] = False
                save_type = "disable"
            elif enable_account:
                user_edits["is_active"] = True
                save_type = "enable"
            updated_user = UserManager.save_user(user_edits, save_type)
            print(f"Updated user: {updated_user}")
            return redirect(url_for("homepage"))
        return render_template("error.html")

    @staticmethod
    @__app.route('/admin_dashboard')
    @login_required
    @UserManager.role_required("admin")
    def admin_dashboard():
        audit_log = AdminManager.get_audit_log()  # I would probably want to sequence by 25 rows. I should only pull that each time
        # I can take in a range based on the page, as a form or link.
        # For now do page/table design then do that.
        return render_template("admin/admin_dashboard.html", audit_log=audit_log)

    @staticmethod
    @__app.route('/revert_change', methods=["POST"])
    @login_required
    @UserManager.role_required("admin")
    def revert_change():
        revert_id = request.form.get("revert_id")
        print(f"{revert_id=}")
        revert_entry = AdminManager.get_audit_entry(revert_id)
        print(f"{revert_entry=}")
        return render_template("admin/check_revert_change.html", revert_entry=revert_entry)

    @staticmethod
    @__app.route('/check_delete_user', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def check_delete_user():
        delete_user = ""
        if "user_id" in request.form:
            delete_user = UserManager.lookup_user_id(ObjectId(request.form["user_id"]))
        if delete_user:
            print("Delete user selected")
        else:
            print("No user found to delete.")
        return render_template("admnin/check_delete_user.html", user=delete_user)

    @staticmethod
    @__app.route('/do_delete_user', methods=['POST'])
    @login_required
    @UserManager.role_required("admin")
    def do_delete_user():
        delete_user_id = ""
        if "user_id" in request.form:
            delete_user_id = ObjectId(request.form["user_id"])
        delete_user = UserManager.lookup_user_id(delete_user_id)
        delete_name = delete_user.name
        UserManager.delete_user(delete_user_id)
        return render_template("admin/confirm_user_deleted.html", delete_name=delete_name)
