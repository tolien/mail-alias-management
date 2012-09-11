#!/usr/bin/python

import unittest
import sqlite3
import aliases
import os

class TestAliases(unittest.TestCase):
    def setUp(self):
        self.test_data_root = 'test_data/Aliases/'
        self.reader = aliases.Aliases()
        self.reader.config_file = self.test_data_root + 'config.ini'
        self.db_path = self.test_data_root + 'test.db'
        self.reader.dbc = sqlite3.connect(self.db_path, isolation_level=None)
        self.reader.config_parser()
        self.setupDB()

    
    def setupDB(self):
        table_name = self.reader.config_reader.get_value('table')
        alias_field = self.reader.config_reader.get_value('where_field')
        destination_field = self.reader.config_reader.get_value('select_field')
        
        self.reader.dbc.execute('''CREATE TABLE %s
            (%s text, %s text)''' % (table_name, alias_field, destination_field))
        self.reader.dbc.execute('''INSERT INTO %s
            VALUES ('bob@bob.com', 'robert@bob.com')''' % (table_name))

    def tearDown(self):
        os.unlink(self.test_data_root + 'test.db')
                    
    def test_get_aliases(self):
        aliases = self.reader.get_aliases()
        self.assertEquals(1, len(aliases))
        
    def test_delete_aliases(self):
        aliases = self.reader.delete_alias('bob@bob.com')
        self.assertEquals(0, len(self.reader.get_aliases()))

if __name__ == "__main__":
    unittest.main()
