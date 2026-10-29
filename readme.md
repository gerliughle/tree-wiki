Building bonsai knowledge repository, built on a tree-based data structure. 
Each new branch has a parent, automatically inheriting all of its data. This happens through leaves, which are attached to branches. New leaves can overwrite the data on inherited leaves, otherwise the parent's will be displayed. This allows specific info to build on foundational knowledge, avoiding repitition, providing context, and allowing both best practicies and specifics. 


Structure:
* Logic programmed in Python
* Developed using Flask Python Server
* Login, Cookies, Sessions use Flask-login
* Password Security uses bcrypt
* Profanity detection using alt-profanity-check and better_profanity
* HTML control with Jinja templates
* CSS design framework from Bootstrap
* Database is cloud-based, NoSQL dictionary using MongoDB Atlas
* Web Server is Raspberry PI running on Ubuntu Server
* Server secured with Uncomplicated Firewall (ufw) and passwordless login
* Production server uses Gunicorn
* Front-end routing/https uses Cloudflared tunnel
* Domain name from CloudFlare
* Multiple CloudFlare security layers including AI labrynth, Rate Limiting, Turnstile

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
* Fixed seasons appearing on stack column, colored seasons
* Edit page default text should be old text.
* Branch creation/editing checks for duplicate names
* Leaves only allow one or all seasons, with all season selector. 
* Don't allow leaves with no phases
* Implement custom error page/flashes:
  * Setup custom error messages instead of redirect to error page.
  * Utilize flask flash message and bootstrap alert for errors and messaging, avoiding error pages
  * Server side input validation for all text inputs.
  * Profanity checks
  * Server side input cleaning
* Data validation:
  * CloudFlare Turnstile
  * Rate limit
* Removed lots of old edit pages/code that are obsolete from Edit Mode.
* Removed confirmation pages due to flash messaging
*   * ObjectId validation function.
* Major change to 'killswitch'. All leaves now must be valid with at least 1 season, entry, and phase per entry. 
  * If you want to stop a leaf from being inherited, you can toggle "Allow Inheriting" on the edit page. 
  * This prevents child branches from using this leaf in their care guides. A badge will be shown on leaves like this. 
  * You can toggle this back on later. This allows visibility of killswitches. There may be some old leaves that break rules. 
  * I also don't think you need entry text, for example, if you just want to say 'wire' in 'winter' for 'all phases'
* User-uploaded branch images:
  * image is uploaded, using modal form
  * Validate rules (size, hd space. later, # of submissions?)
  * validate extension/header
  * save database entry
  * save image with id filename
  * check logs and log display
  * Photos can have captions
* Image moderation
  * Page and route built, access control
  * Set quality/caption/save routes
  * Sort by date
  * Show branch & user image stats
  * Approval switch, disable, delete routes
* Image Carousel
  * Get up to 5 approved images, sorted by quality
  * Display them in a carousel
  * If 1 image, remove buttons
  * Auto crop images, rounded corners.
  * If caption, display with a backdrop


To-Do:

* P0:
  * Think simpler entries focused on timing, with expandable info. The default layout should be more like a calendar. 
    * Not far off from this really, just cut all unnecessary info, maybe make the view more compact. Altho it would
    * be cool to hide title, and really just have task arranged by season.
    * Tricky to also manage the mobile view with this though
    * You had an airtable-esque idea of like limiting the length of text. and then being able to click leaves
    * and it pops up a modal or something to see it all. 
* Data validation:
  * Client side form validation, and field tuning (autocomplete, etc).
  * jinja escapes check
  * Honeypot field for login, edit forms.
  * Commented out logic-level ObjectId validations. If that works after a while, can delete.


* Photos
  * build moderation page
    * filter view: show active/inactive and approved/needs_approval/unapproved
    * Images for parents without images
    * Random selection for more than 5 valid choices
    * backup db
    * fix size error 413 thing
* Paginate admin log
* Clean up branch edit button forms
* Homepage
* About page
* Logo


P1:
* Mobile menu fix.. logout/dark toggle.
* if logged out, can i redirect to homepage when accessing bad page? 
* redo 404/etc pages? 
* Cat/Leaf Schema
* Can i fully collapse into like, 'wire' in the season one line? Or is this even another section of the page?
* log filters/searching
* site searching
* Photos
  * Thumbnails
  * Galleries
  * Zoom in image view

Later:
* TBH, the whole revert thing... it probably just makes sense to go full git, and save versions of everything. 
  * It seems like this could be tricky or hard. I need to keep same _id so the trees don't get really fucked
  * So they'd all be stored in the same object, but i'd only want to call the latest one for page views, but call
  * them all for admin/mod stuff
* User stats, awards, gamification, authorship.
* Can likely make check_disable/delete_branch/leaf page a single smart template.
* Mod role: Editors edit pages, mods can revert/disable, and admins can manage users
* Tree View. Started, but ugly
* About page/legend/guide/phase description
* change password (require fresh login)
* forget password
* Alternate User Id to allow for id changing.. see flask-login
* Dark mode - svg color tweaks
* User edit mode - change role, disable, delete users. maybe that's only allowed for even another role
  *  What if... individual accounts can have their own version of a tree, with notes, their own prefernces, etc. 
  * Then they can submit them to be accepted or something
* Dark/Light Mode - color palette adjustments
* Category Collapse - arrow direction change
* Have phases be UserState variable
* Thoughts on non-bonsai applicability. Season = category, phase = filter
* Tooltips
* user emails
 redesign to be less round and floaty. a bit more table-y would be more functional
* Data entry
* Non admin edit/suggestion
* Temp Selector system


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
