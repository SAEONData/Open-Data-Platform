import re


def make_object_name(title: str):
    """
    Return a string suitable for use as a unique object name, generated from
    a user-entered title, by lowercasing and converting any sequence of non-
    letter/digit chars to a hyphen.
    """
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
