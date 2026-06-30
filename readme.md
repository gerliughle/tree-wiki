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


Problems:
Problem 0:
Dynamic site doesn't update on filters. Gonna drop JS and stick to flask.
Also will cut season filter it is pointless. 
Need to have phase selctor be a form (with apply button)
Then it reloads the page, pushing the phase list with GET to update the URL.

Need to load page initially by sending all phases i guess



Problem 1:
Phase inheritance. (May also apply to seasons)
It does not apply to seasons actually. Those should overwrite so you can change them. 
The general inheritance rule is that child subcategories replace parent ones.
But a parent could have a leaf of all 3 phases.
If the child only has phase one, what does it display for phase 2/3?
What if parent has repot phase 1, then you write repot phase 2? 

I think that a new leaf could inherit phases it does not have. 
Ok, lets say that you do that AND change a season. 

Repot phase 1 in spring for bonsai
p afras, repot phase 123 in Summer.
it overwrites.

p afras repot phase 2 in summer. 
i think it would inerit the phase 1 in spring. But honestly that is a case of bad data, you shold rewrite all phases.
Actually though, a leaf can only have one season list. 
And only one leaf per subcategory. 
Is that an issue? If you want to do the same task at different seasons for different phases, you can't. 
Maybe you just have to name them different things

Unless you do allow multiple of same subcategory with different properties.
No, just rename it. 

So subcategories can have multiple entries for different phases, but not different seasons? 
So really a subcategory has seasons, but individual entries can have different phases. 
Leaves may need to be broken into two parts. 

It might make sense to build out more dummy data. I think for the most part rules can change later. 
This could impact like, having different breadcrumbs for multiple entries on one leaf. 


Problem 2: 
How to display different leaves on same subcategory.
bootstrap card list items maybe

