#!/usr/bin/python

import unittest
import PostfixConfig
import os

class TestPostfixConfigReader(unittest.TestCase):
    def setUp(self):
        self.test_data_root = 'test_data/PostfixConfig/'
        os.chmod(self.test_data_root + 'inaccessable-aliases.cf', 0000)
    
    def tearDown(self):
        os.chmod(self.test_data_root + 'inaccessable-aliases.cf', 0700)
        
    def test_file_not_exist(self):
        reader = PostfixConfig.Reader('file-which-does-not-exist')
        self.assertRaises(IOError, reader.get_value, 'foo')
        
    def test_file_no_permission(self):
        reader = PostfixConfig.Reader(self.test_data_root + 'inaccessable-aliases.cf')
        self.assertRaises(PostfixConfig.NoPermissionException, reader.get_value, 'foo')

    def test_key_not_existing(self):
        reader = PostfixConfig.Reader(self.test_data_root + 'accessable-aliases.cf')
        self.assertRaises(KeyError, reader.get_value, 'foo')

    def test_key_existing(self):
        reader = PostfixConfig.Reader(self.test_data_root + 'accessable-aliases.cf')
        self.assertEqual(reader.get_value('where_field'), 'alias')
        
    def test_extra_equals(self):
        reader = PostfixConfig.Reader(self.test_data_root + 'extra-equals.cf')
        self.assertEqual(reader.get_value('select_field'), 'destination = cheese')

if __name__ == "__main__":
    unittest.main()
