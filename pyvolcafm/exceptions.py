"""Exceptions"""

class Error(Exception):
    pass

class OutOfRangeError(Error):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value
