"""Reader
Abstraction around the Postfix virtual users config files

Functions:
read_values: returns all config for a file
get_value: returns a specific config item for a file
"""

import os

class FileAccessError(Exception):
    NO_SUCH_FILE = 1
    NO_PERMISSION = 2
    def __init__(self, filename, cause):
        Exception.__init__(self)
        self.filename = filename
        self.cause = cause

    def __str__(self):
        if self.cause == self.NO_SUCH_FILE:
            return "File %s does not exist" % self.filename
        elif self.cause == self.NO_PERMISSION:
            return "No permission to read %s" % self.filename
        else:
            return "Unknown error"

    def get_filename(self):
        return self.filename

class Reader:
    def __init__(self, filename):
        self.filename = filename

    def read_values(self):
        """Return all the config in the given file as a dictionary."""
        values = {}

        file_exists = os.access(self.filename, os.F_OK)
        can_read_file = os.access(self.filename, os.R_OK)
        if file_exists:
            if not can_read_file:
                raise FileAccessError(self.filename,
                                      FileAccessError.NO_PERMISSION)
            else:
                file_desc = open(self.filename)

            for line in file_desc:
                pieces = line.split('=', 1)
                if len(pieces) == 2:
                    key = pieces[0].strip()
                    value = pieces[1].strip()
                    values[key] = value

            file_desc.close()
            return values
        else:
            raise FileAccessError(self.filename, FileAccessError.NO_SUCH_FILE)

    def get_value(self, key):
        """Get a specific config item from the config file specified."""

        all_values = self.read_values()
        return all_values[key]
