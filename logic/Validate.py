import os
import shutil
import imghdr
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
    UPLOAD_EXTENSIONS = [".jpg", ".png", ".jpeg"]

    @staticmethod
    def make_objectid(obj_id):
        """ Returns ObjectId from string or ObjectId"""
        if not obj_id:
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

        Returns: True/False if passes validation, the text, and an error message.

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
            if not all(char.isalpha() or char.isspace() for char in text):
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
            text = text.lower()
        elif kind == "password":
            pass
        elif kind == "title":
            print(f"Title: {text}")
            text = text.title()
            print(f"New title: {text}")
        elif kind == "text":
            text = text.capitalize()

        return text

    @staticmethod
    def get_free_disk_gb(path):
        total, used, free = shutil.disk_usage(path)
        return free / (1024 ** 3)


    @classmethod
    def validate_image(cls, image_file):
        """ Validates strings for user inputs to accept or reject inputs.

        Returns tuple: True/False if passes validation, the image extension and an error message.

        image_file should be the image from the form.
        Checks that there is HD space available.
        Checks that it has a valid image extension
        Checks that the file header matches the extension
        """
        from ui.WebUI import WebUI
        if cls.get_free_disk_gb(WebUI.USER_IMAGES_PATH) < WebUI.MIN_HD_SPACE_GB*3:
            return False, None, "Error, disk space full. Please contact site admin."

        image_ext = os.path.splitext(image_file.filename)[1]
        stream = image_file.stream
        if image_ext not in cls.UPLOAD_EXTENSIONS:
            return False, image_ext, f"Image extension {image_ext} not supported."
        header = stream.read(512)
        stream.seek(0)
        img_format = imghdr.what(None, header)
        if not img_format:
            return False, "Error with image. Please try again."
        return True, image_ext,""




