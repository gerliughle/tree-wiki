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


Flask Routes:
* index.html
* Login
* Create Branch
* Edit Branch
* Delete Branch

Templates:
* index.html >> should be branch.html
* template.html
* navbar.html
* category.html
* leaf.html


Branch page To-Do:
* Create subcategory setup to allow multiple shared leaves in one subcategory
* for different phases.
* redesign to be less round and floaty. a bit more table-y would be more functional
* Make category order consistent
* I removed season filtering, but could be added if it expands column view to be more usable.

Then other to-dos:
* Editing Data system
* Homepage
* Integrate edit links into page design (add child, clone branch, etc)
* Tree View
* About page/legend
* Tooltips
* input validation
* Temp Selector system


Bugs and fixes:

* need to make it so inherited leaves are NOT the same as matching ones
* killswitch evaluation needs work
* breadcrumbs are broken
* if i delete a branch, i also need to delete all its leaves.


been skipping any validations but it is important:
* checking for any form errors
* avoiding duplicates
* avoiding no phase/no season submissions
* avoiding matching subcat for leaves


