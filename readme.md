Building bonsai knowledge repository, built on a tree-based data structure. 
Each new branch has a parent, automatically inheriting all of its data. This happens through leaves, which are attached to branches. New leaves can overwrite the data on inherited leaves, otherwise the parent's will be displayed. This allows specific info to build on foundational knowledge, avoiding repitition, providing context, and allowing both best practicies and specifics. 


Structure:
* Logic programmed in Python
* Developed using Flask Python Server
* Login, Cookies, Sessions use Flask-login
* Password Security uses bcrypt
* HTML control with Jinja templates
* CSS design framework from Bootstrap
* Database is cloud-based, NoSQL dictionary using MongoDB Atlas
* Web Server is Raspberry PI running on Ubuntu Server
* Server secured with Uncomplicated Firewall (ufw) and passwordless login
* Production server uses Gunicorn
* Front-end routing/https uses Cloudflared tunnel
* Domain name from CloudFlare

Done:
* Branch Class
* Leaf Class
* StaticData provides temp data
* TreeEngine for engine logic
* UserManager
* Flask implemented
* Bootstrap implemented
* Card padding
* Branch page pulls from database, passed variables
* Hide season section if irrelevant
* Collapse category. 
* Phase selector
* Season Selector
* Appropriate breadcrumbs for leaves
* Functional breadcrumbs
* Breadcrumb design/sizing
* Auto hiding categories/seasons doesn't work with the JS filters.
* Database backup
* Logins/accounts
* Create child section in header
* Header images
* Page footer
* if i delete a branch, i also need to delete all its leaves.
* breadcrumbs are broken
* need to make it so inherited leaves are NOT the same as matching ones
* Editing Data system
* show season on leaf editing page
* Create edit page version of branch (add child, clone branch, etc)
* Create subcategory setup to allow multiple shared leaves in one subcategory for different phases.
* Constant category order/list
* Update login system to flask-login
* Dark Mode
* Have edit mode be a session variable, not page
* Admin page access.. ensure edit mode/pages are protected.
* Disabling users
* Audit logs, before/after states
* Fixed gunicorn worker count, it was not updating edits consistently. With lots of users, this will need a solution.
* Add is_active property to leaves/branches to have a disable option vs delete
* Enable www routing
* Created update_class method to add properties, fix blanks, etc. 
* Increase secret key security
* Responsive design for no picture
* Set up git for dev/main
* Add routes/buttons/page designs. Only enable delete for admins
* * Add disable features for branches/leaves:
  * Update pull logic to skip disabled stuff - pretty sure is done
  * Updated branch parent_id to check is_active. If so, checks up the chain.
  * Updated read_data to pull all/active branches and leaves. This keeps disabled branches in memory for gap filling
  * Big rewrite of database save methods, so its one shared method across all objects/tasks except delete.
  * Updated user, branch, leaf logic to use consolidated create/edit/enable/disable logic.
  * Made smarter buttons on admin dashboard for appropriate actions. 
  * Added delete for admin roles. 
  * Reverting branch/leaf/user edits should work now! Admin dashboard should be fully functional!!! 
* Tightened up leaf cards
* Leaf collapse button


To-Do:
* How do i disable leaves that have no-phase killswitches? Re-think these, they are hidden and not really possible for users to work with.

* I removed leaf breadcrumb, it would be cool to have a chain of subcat edits, but need leaf-specific bredcrumbs
* Admin Log - pagination
* change password (require fresh login)
* forget password
* Alternate User Id to allow for id changing.. see flask-login
* Edit page default text should be old text.
* Dark mode - svg color tweaks
* User edit mode - change role, disable, delete users. maybe that's only allowed for even another role
* Dark/Light Mode - color palette adjustments
* Category Collapse - arrow direction change
* Ensure you're using jinja escapes appropriately
* Have phases be UserState variable
* Homepage
* Tree View. Started, but ugly
* About page/legend/guide/phase description
* Thoughts on non-bonsai applicability. Season = category, phase = filter
* Tooltips
* input validation
* user emails
 redesign to be less round and floaty. a bit more table-y would be more functional
* Data entry
* Find pictures somehow
* Non admin edit/suggestion
* Temp Selector system

been skipping any validations but it is important:
* checking for any form errors
* avoiding duplicates
* avoiding no phase/no season submissions
* avoiding matching subcat for leaves


next up: tree view

this should be a component that can be included anywhere. 
would make sense to be able to separate it out as a possible breadcrumb/children replacement
so have upper/lower sort of thing
could have stats like # of leaves and stuff. 


For non-bonsai applicability:
- By using multiple roots, you can have multiple, non connected trees if they don't share categories.
- Consistent categories should be how things are determined to belong in the same tree. 
- Maybe there is a tree of trees
- Within the bonsai tree, there are :
-- ~7 static categories
-- as many subcategories as needed
-- 4 seasons (leaf grouping?)
-- 3 phases (filters)
-- Each leaf has only one season setting, but can have entries with as many filter arrangements as desired. But only 1 leaf per subcategory.
- If you made it possible for trees to customize their category, filter, and group settings, it would be pretty adaptable. 
- I'm not sure how the seasons grouping would apply to other data sources, and design would need to be rethought or more responsive for different #'s of groups
