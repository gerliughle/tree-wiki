from bson import ObjectId
from bson.errors import InvalidId
from profanity_check import predict
from wordsegment import load, segment
from better_profanity import profanity
from flask import flash
from bson import ObjectId
from bson.errors import InvalidId
import string

class Validate:

    load()
    profanity.load_censor_words()

    @staticmethod
    def validate_objectid(obj_id):
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
                       clean_profile=None,
                       check_profanity=True):
        """ Set rules for input validation.

        Returns tuple: True/False if passes validation, the text, and an error message.

        text: the text string to be validated
        field_name: The field the text is for, to return appropriate error.
        min_length: min_char length. If 0, then field can be blank.
        max_length: max_char length.
        check_profanity: Check text through profanity filter. Returns False if profane.
        clean_profile: "username", "password", "title", "text" will check against rules and apply some cleaning.
            "username" is all lowercase, no spaces, limited characters.
            "password" is no spaces
            "title" uses title capitalization, no special characters.
            "text" uses first capitalization
        """

        text = text.strip()
        field_name = field_name.capitalize()
        if text is None and min_length > 0:
            return False, text, f"{field_name} cannot be empty."

        if check_profanity:
            profane = cls.check_profanity(text)
            if profane:
                return False, text, f"{field_name} was invalid. Please try again."

        if clean_profile == "username":
            text = text.lower()
            text = text.replace(" ", "")
            for letter in text:
                if letter not in [string.ascii_lowercase, string.digits, ['_', '-']]:
                    return False, text, f"{field_name} contains invalid characters. Please try again."
        elif clean_profile == "password":
            for letter in text:
                if letter == " ":
                    return False, text, f"{field_name} cannot have spaces. Please try again."
        elif clean_profile == "title":
            text.title()
            for letter in text:
                if letter not in string.ascii_letters:
                    return False, text, f"{field_name} can only contain letters. Please try again."
        elif clean_profile == "text":
            text.capitalize()


        if len(text) < min_length:
            return False, text, f"{field_name} is too short."
        elif len(text) > max_length:
            return False, text, f"{field_name} is too long."
        return True, text, ""

