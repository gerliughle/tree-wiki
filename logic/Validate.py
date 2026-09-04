from profanity_check import predict
from wordsegment import load, segment
from better_profanity import profanity
from bson import ObjectId
from bson.errors import InvalidId
import string


class Validate:
    load()
    profanity.load_censor_words()
    USERNAME_CHARS = set(string.ascii_lowercase + string.digits + "-_")


    @staticmethod
    def make_objectid(obj_id):
        """ Returns ObjectId from string or ObjectId"""
        if not obj_id:
            print("validate_objectid - Error: No id provided.")
            return None
        try:
            return ObjectId(obj_id)
        except (InvalidId, TypeError):
            print("validate_objectid - Error: Invalid ObjectId.")
            return None

    @staticmethod
    def normalize_text(text):
        text = text.lower()
        char_map = {
            '@': 'a',
            '4': 'a',
            '0': 'o',
            '1': 'i',
            '!': 'i',
            '3': 'e',
            '$': 's',
            '5': 's',
            '7': 't'
        }
        for char, replacement in char_map.items():
            text = text.replace(char, replacement)
        return text

    @classmethod
    def check_profanity(cls, text):
        """ Checks for profanity on text inputs. """

        clean_text = cls.normalize_text(text)
        words = segment(clean_text)
        segmented_words = " ".join(words)
        has_profane_word = profanity.contains_profanity(segmented_words)
        has_profane_text = predict([segmented_words])
        if has_profane_word or has_profane_text:
            return True
        else:
            return False

    @classmethod
    def validate_input(cls,
                       text: str,
                       field_name,
                       min_length=0,
                       max_length=1000,
                       kind=None,
                       check_profanity=True,
                       clean=True):
        """ Validates strings for user inputs to accept or reject inputs.

        Returns tuple: True/False if passes validation and an error message.

        text: the text string to be validated
        field_name: The field the text is for, to return appropriate error.
        min_length: min_char length. If 0, then field can be blank.
        max_length: max_char length.
        check_profanity: Check text through profanity filter. Returns False if profane.
        kind: "username", "password", "title", "text" will be checked against unique rules.
            "username" - no spaces, limited characters.
            "password" - no spaces
            "title" - no special characters.
            "text" - currently has no rules.
        """

        if clean:
            text = cls.clean_input(text, kind)

        field_name = field_name.capitalize()
        if text is None and min_length > 0:
            return False, text, f"{field_name} cannot be empty."

        if check_profanity:
            profane = cls.check_profanity(text)
            if profane:
                print("Profanity found. Yikes.")
                return False, text, f"{field_name} was not accepted. Please try again."

        if kind == "username":
            for char in text:
                if char not in cls.USERNAME_CHARS:
                    return False, text, f"{field_name}s can only contain lowercase letters, numbers, and dashes. Please try again."

        elif kind == "password":
            for char in text:
                if char == " ":
                    return False, text, f"{field_name} cannot have spaces. Please try again."

        elif kind == "title":
            if not text.isalpha():
                return False, text, f"{field_name} can only contain letters. Please try again."
        elif kind == "text":
            pass

        if len(text) < min_length:
            return False, text, f"{field_name} is too short."
        elif len(text) > max_length:
            return False, text, f"{field_name} is too long."

        return True, text, ""

    @classmethod
    def clean_input(cls,
                    text: str,
                    kind=None):
        """ Cleans string inputs for inputs.

        Returns cleaned text. Strips all text.

        text: the text string to be validated
        clean_profile: "username", "password", "title", "text" will check against rules and apply some cleaning.
            "username" is all lowercase.
            "password" has nothing.
            "title" uses title capitalization
            "text" uses first capitalization
        """
        text = text.strip()

        if kind == "username":
            text.lower()
        elif kind == "password":
            pass
        elif kind == "title":
            text.title()
        elif kind == "text":
            text.capitalize()

        return text

