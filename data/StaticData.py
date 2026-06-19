from bson import ObjectId

# =====================================================================
# 1. GENERATE STATIC OBJECTIDS FOR LINKING
# =====================================================================
# We generate these upfront so we can manually link branches to parents,
# and leaves to branches, exactly like MongoDB would store them.

ID_TRUNK = ObjectId()
ID_DECIDUOUS = ObjectId()
ID_MAPLE_GENUS = ObjectId()
ID_JAPANESE_MAPLE = ObjectId()
ID_AUTHOR = ObjectId()

# =====================================================================
# 2. MOCK BRANCHES DATA
# =====================================================================
# Representing the hierarchical structure of the wiki tree.
# Notice how each child points to its parent via 'parent_id'.

mock_branches = [
    {
        "_id": ID_TRUNK,
        "author_id": ID_AUTHOR,
        "name": "Bonsai",
        "parent_id": None
    },
    {
        "_id": ID_DECIDUOUS,
        "author_id": ID_AUTHOR,
        "name": "Deciduous",
        "parent_id": ID_TRUNK
    },
    {
        "_id": ID_MAPLE_GENUS,
        "author_id": ID_AUTHOR,
        "name": "Maple",
        "parent_id": ID_DECIDUOUS
    },
    {
        "_id": ID_JAPANESE_MAPLE,
        "author_id": ID_AUTHOR,
        "name": "Japanese Maple",
        "parent_id": ID_MAPLE_GENUS
    }
]

# =====================================================================
# 3. MOCK LEAVES DATA (USER-GENERATED INFO BLOCKS)
# =====================================================================
# These contain the actual care information.
# They map to a branch via 'branch_id' and contain categorical & seasonal tags.

mock_leaves = [

    # -----------------------------------------------------------------
    # LEVEL 1: TRUNK LEAVES (Global Baselines)
    # -----------------------------------------------------------------
    {
        "_id": ObjectId(),
        "branch_id": ID_TRUNK,
        "author_id": ID_AUTHOR,
        "category": "Watering",
        "subcategory": "General Watering",
        "seasons": ["Spring", "Summer", "Fall", "Winter"],  # All Seasons
        "phases": ["1st", "2nd", "3rd+"],
        "text": "Standard baseline rule: Water thoroughly when the topsoil looks slightly dry. Never let the rootball dry out completely."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_TRUNK,
        "category": "Environment",
        "subcategory": "Frost Protection",
        "seasons": ["Winter"],
        "phases": ["1st", "2nd", "3rd+"],
        "text": "Protect the root system from sustained freezing temperatures. Move trees into an unheated garage, shed, or cold frame."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_TRUNK,
        "category": "Potting",
        "subcategory": "Repotting",
        "seasons": ["Spring"],
        "phases": ["1st", "2nd", "3rd+"],
        "text": "Repot right as the buds begin to swell but before leaves unfurl. Comb out old soil and trim back circling roots."
    },

    # -----------------------------------------------------------------
    # LEVEL 2: DECIDUOUS BRANCH LEAVES
    # -----------------------------------------------------------------
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_DECIDUOUS,
        "category": "Pruning",
        "subcategory": "Structural Pruning",
        # TEST CASE: Multi-season leaf (Appears in both Spring and Fall)
        "seasons": ["Spring", "Fall"],
        "phases": ["2nd", "3rd+"],
        "text": "Cut back thick, unwanted structural branches. Deciduous trees heal best from major cuts during early spring before sap flow, or late fall during dormancy."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_DECIDUOUS,
        "category": "Pruning",
        "subcategory": "Defoliation",
        "seasons": ["Summer"],
        "phases": ["2nd", "3rd+"],
        "text": "Cut away 100% of large leaves on healthy trees in mid-summer. This forces a second flush of smaller leaves and increases branch ramification."
    },

    # -----------------------------------------------------------------
    # LEVEL 3: MAPLE GENUS LEAVES
    # -----------------------------------------------------------------
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_MAPLE_GENUS,
        "category": "Environment",
        "subcategory": "Lighting",
        "seasons": ["Summer"],
        "phases": ["1st", "2nd", "3rd+"],
        "text": "Maples have thin delicate leaves. Provide 50% shade cloth during peak mid-summer afternoon sun to prevent leaf scorching."
    },

    # -----------------------------------------------------------------
    # LEVEL 4: JAPANESE MAPLE LEAVES (Specific Overrides)
    # -----------------------------------------------------------------
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_JAPANESE_MAPLE,
        "category": "Pruning",
        "subcategory": "Controlling Growth",
        "seasons": ["Spring", "Summer"],
        "phases": ["2nd", "3rd+"],
        "text": "Pinch out the central growth tip of fresh shoots down to the first pair of leaves. This stops long leggy nodes from ruining the silhouette."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_JAPANESE_MAPLE,
        "category": "Pruning",
        "subcategory": "Subcategory 2",
        "seasons": ["Spring", "Summer"],
        "phases": ["2nd", "3rd+"],
        "text": "Another subcategory in Pruning."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_JAPANESE_MAPLE,
        "category": "Potting",
        "subcategory": "Repotting",
        # TEST CASE: Overwrites the Trunk's 'Repotting' data entirely
        "seasons": ["Spring"],
        "phases": ["1st"],
        "text": "Young Japanese Maples are incredibly vigorous. Repot them every single year to prevent them from becoming severely root-bound."
    },
    {
        "_id": ObjectId(),
        "author_id": ID_AUTHOR,
        "branch_id": ID_JAPANESE_MAPLE,
        "category": "Pruning",
        "subcategory": "Defoliation",
        # TEST CASE: Rule 6 Kill-switch. empty seasons & phases.
        # This should stop 'Defoliation' from climbing to the Deciduous level,
        # ensuring nothing shows up on the screen for Japanese Maple defoliation.
        "seasons": [],
        "phases": [],
        "text": "KILL_SWITCH: Do not defoliate Japanese Maples; they do not recover well compared to other deciduous trees."
    }
]


# =====================================================================
# 4. DATA HELPER FUNCTIONS FOR YOUR LOGIC ENGINE
# =====================================================================
# These simulate database queries while you are offline.

def get_all_branches():
    return mock_branches


def get_all_leaves():
    return mock_leaves