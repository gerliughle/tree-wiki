Building bonsai knowledge repository, built on a tree-based data structure. 
Each new branch has a parent, automatically inheriting all of its data. This happens through leaves, which are attached to branches. New leaves can overwrite the data on inherited leaves, otherwise the parent's will be displayed. This allows specific info to build on foundational knowledge, avoiding repitition, providing context, and allowing both best practicies and specifics. 


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


Templates:
* index.html >> should be branch.html
* template.html
* navbar.html
* category.html
* leaf.html


Branch page To-Do:

* redesign to be less round and floaty. a bit more table-y would be more functional
* Make category order consistent
* I removed season filtering, but could be added if it expands column view to be more usable.

Then other to-dos:

* Dark Mode
* Dark mode - svg color tweaks
* Dark/Light Mode - color palette adjustments
* Category Collapse - arrow direction change
* Admin page access.. ensure edit mode/pages are protected.
* Have edit mode be a UserState variable, not page
* Have phases be UserState variable
* Homepage
* Increase secret key security?
* Tree View. Started, but ugly
* About page/legend/guide/phase description
* Thoughts on non-bonsai applicability. Season = category, phase = filter
* Tooltips
* input validation
* user emails
* change password (require fresh login)
* forget password
* Data entry
* Non admin edit/suggestion
* Temp Selector system
* Alternate User Id to allow for id changing.. see flask-login


Bugs and fixes:
* killswitch evaluation needs work
* show season on leaf editing page



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
