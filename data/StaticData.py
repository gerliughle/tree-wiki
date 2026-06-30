from bson import ObjectId
from logic.User import User

josh_pw = User.hash_password("oiufdsa1")
user_pw = User.hash_password("oiufdsa2")

mock_users = [
    {
        "username": "josh",
        "pw_hash": josh_pw,
        "role": "admin"
    },
    {
        "username": "public_user",
        "pw_hash": user_pw,
        "role": "user"
    }
]

mock_branches = [
    {
        "author_id": None,
        "name": "Bonsai",
        "description": "A general care guide for Bonsai trees. These tips are widely applicable,"
                       "but will often be replaced by more specific care info. Beyond care tips,"
                       "fundamental care concepts can be shared here to give background knowledge.",
        "image": "bonsai.jpg"
    },
    {
        "author_id": None,  # Parent: Bonsai
        "name": "Broadleaf",
        "description": "A tree with leaves.",
        "image": "broadleaf.jpg"
    },
    {
        "author_id": None,  # Parent: Broadleaf
        "name": "Deciduous Broadleaf",
        "description": "Deciduous trees lose their leaves or needles in Winter. They require this cycle, so "
                       "keeping them in temperate climates or indoors can hurt them long term. Deciduous "
                       "trees are often prized for their Fall colors, and their bare branches in Winter "
                       "allow an opportunity to appreciate their intricate branch structure. Many Deciduous "
                       "trees are specifically displayed during their dormant period in winter.",
        "image": "deciduous_broadleaf.jpg"
    },
    {
        "author_id": None,  # Parent: Broadleaf Deciduous
        "name": "Maple",
        "description": "A very popular genus for bonsai, Maples have thousands of varieties, many of which are popular "
                       "for Bonsai. Japanese Maples are extremely popular, and more people are experimenting with "
                       "maples native to their regions. Bonsai-suitable maples should not have excessively large leaves "
                       "or long internodes.",
        "image": "maple.jpg"
    },
    {
        "author_id": None,  # Parent Maple
        "name": "Japanese Maple",
        "description": "One of the most popular Bonsai subjects, there are hundreds of varieties of Japanese Maples. "
                       "Many have unique care needs and characteristics, and some are not well suited for Bonsai. "
                       "The standard Acer Palmatum is a vigorous and popular species. Many JM's are prized for their "
                       "small leaves, varied colors throughout the year, and capabilities for finely ramified "
                       "canopies. ",
        "image": "japanese_maple.jpg"
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
        # "_id": ObjectId(),
        "author_id": None,
        # "branch_id": ID_TRUNK,
        "category": "Watering",
        "subcategory": "General Watering",
        "seasons": ["Spring", "Summer", "Fall", "Winter"],  # All Seasons
        "entries": [
            {
                "text": "Standard baseline rule: Water thoroughly when the topsoil looks slightly dry. Never let the rootball dry out completely.",
                "phases": ["1st", "2nd", "3rd+"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        # "branch_id": ID_TRUNK,
        "category": "Environment",
        "subcategory": "Frost Protection",
        "seasons": ["Winter"],
        "entries": [
            {
                "text": "Protect the root system from sustained freezing temperatures. Move trees into an unheated garage, shed, or cold frame.",
                "phases": ["1st", "2nd", "3rd+"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        # "branch_id": ID_TRUNK,
        "category": "Potting",
        "subcategory": "Repotting",
        "seasons": ["Spring"],
        "entries": [
            {
                "text": "Repot right as the buds begin to swell but before leaves unfurl. Comb out old soil and trim back circling roots.",
                "phases": ["1st", "2nd", "3rd+"]
            }
        ]
    },

    # -----------------------------------------------------------------
    # LEVEL 2: DECIDUOUS BRANCH LEAVES
    # -----------------------------------------------------------------
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_DECIDUOUS
        "category": "Pruning",
        "subcategory": "Structural Pruning",
        # TEST CASE: Multi-season leaf (Appears in both Spring and Fall)
        "seasons": ["Spring", "Fall"],
        "entries": [
            {
                "text": "Cut back thick, unwanted structural branches. Deciduous trees heal best from major cuts during early spring before sap flow, or late fall during dormancy.",
                "phases": ["2nd", "3rd+"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_DECIDUOUS
        "category": "Pruning",
        "subcategory": "Defoliation",
        "seasons": ["Summer"],
        "entries": [
            {
                "text": "Cut away 100% of large leaves on healthy trees in mid-summer. This forces a second flush of smaller leaves and increases branch ramification.",
                "phases": ["2nd", "3rd+"]
            }
        ]
    },

    # -----------------------------------------------------------------
    # LEVEL 3: MAPLE GENUS LEAVES
    # -----------------------------------------------------------------
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_MAPLE_GENUS
        "category": "Environment",
        "subcategory": "Lighting",
        "seasons": ["Summer"],
        "entries": [
            {
                "text": "Maples have thin delicate leaves. Provide 50% shade cloth during peak mid-summer afternoon sun to prevent leaf scorching.",
                "phases": ["1st", "2nd", "3rd+"]
            }
        ]
    },

    # -----------------------------------------------------------------
    # LEVEL 4: JAPANESE MAPLE LEAVES (Specific Overrides)
    # -----------------------------------------------------------------
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_MAPLE_GENUS
        "category": "Pruning",
        "subcategory": "Controlling Growth",
        "seasons": ["Spring", "Summer"],
        "entries": [
            {
                "text": "Pinch out the central growth tip of fresh shoots down to the first pair of leaves. This stops long leggy nodes from ruining the silhouette.",
                "phases": ["2nd", "3rd+"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_MAPLE_GENUS
        "category": "Pruning",
        "subcategory": "Structural Pruning",
        "seasons": ["Summer"],
        "entries": [
            {
                "text": "You can take remove a branch but this can cause a burst of new growth. Do this in Summer after the Spring flush to avoid long internodes in the new shoots.",
                "phases": ["2nd", "3rd+"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_MAPLE_GENUS
        "category": "Potting",
        "subcategory": "Repotting",
        # TEST CASE: Overwrites the Trunk's 'Repotting' data entirely
        "seasons": ["Spring"],
        "entries": [
            {
                "text": "Young Japanese Maples are incredibly vigorous. Repot them every single year to prevent them from becoming severely root-bound.",
                "phases": ["1st"]
            }
        ]
    },
    {
        # "_id": ObjectId(),
        "author_id": None,
        "branch_id": None,  # ID_MAPLE_GENUS
        "category": "Pruning",
        "subcategory": "Defoliation",
        # TEST CASE: Rule 6 Kill-switch. empty seasons & phases.
        # This should stop 'Defoliation' from climbing to the Deciduous level,
        # ensuring nothing shows up on the screen for Japanese Maple defoliation.
        "seasons": [],
        "entries": [
            {
                "text": "KILL_SWITCH: Do not defoliate Japanese Maples; they do not recover well compared to other deciduous trees.",
                "phases": []
            }
        ]
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


def get_all_users():
    return mock_users
