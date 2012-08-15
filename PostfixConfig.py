"""Reader
Abstraction around the Postfix virtual users config files

Functions:
read_values: returns all config for a file
get_value: returns a specific config item for a file
"""

class Reader:
    def __init__(self, file):
        self.filename = file
        
    def read_values(self):
        """Return all the config in the given file as a dictionary.
    
        IOError will be thrown if the file referred to does not exist    
        """
        values = {}
    
        file_desc = open(self.filename)
    
        for line in file_desc:
            pieces = line.split('=', 1)
            if len(pieces) == 2:
                key = pieces[0].strip()
                value = pieces[1].strip()
                values[key] = value
    
        file_desc.close()
        return values
    
    def get_value(self, key):
        """Get a specific config item from the config file specified.
    
        Throws IOError if the file cannot be read."""
        all_values = self.read_values()
        return all_values[key]