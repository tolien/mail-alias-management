#!/usr/bin/python

"""Aliases
Accessor

Functions:
read_values: returns all config for a file
get_value: returns a specific config item for a file
"""

import ConfigParser
import PostfixConfig
from argparse import ArgumentParser
import MySQLdb, MySQLdb.cursors

class Aliases:
    def __init__(self):    
        self.dbc = None
        self.config_file = 'config.ini'
        self.config_reader = None

    def config_parser(self):
        config = ConfigParser.SafeConfigParser()

        config.read(self.config_file)
        users_file = config.get('Postfix Config', 'users_file')
        self.config_reader = PostfixConfig.Reader(users_file)
    
    def get_dbc(self):
        if self.config_reader == None:
            self.config_parser()
        user = self.config_reader.get_value('user')
        #host deliberately excluded - use localhost or go home
        password = self.config_reader.get_value('password')
        db_name = self.config_reader.get_value('dbname')
    
        self.dbc = MySQLdb.connect(
            user = user, passwd = password, db = db_name, 
            cursorclass=MySQLdb.cursors.DictCursor)
        
    def get_aliases(self, dest=None, alias=None):
        if not self.dbc:
            self.get_dbc()
        
        table_name = self.config_reader.get_value('table')
        user_field = self.config_reader.get_value('where_field')
        destination_field = self.config_reader.get_value('select_field')

        query = "SELECT %s AS email FROM %s " \
        % (user_field, table_name)
        
        if alias or dest:
            query += "WHERE "
            if alias and len(alias) > 0:
                query += "%s LIKE '%%%s%%' " % (alias_field, alias)
            if alias and dest:
                query += "AND "
            if dest and len(dest) > 0:
                query += "%s LIKE '%%%s%%' " % (destination_field, dest)
        query += "ORDER BY %s ASC" % (user_field)
        
        cursor = self.dbc.cursor()
        cursor.execute(query)
        alias_list = cursor.fetchall()
        return alias_list
        
    def delete_alias(self, alias):
        aliases = self.get_aliases(alias=alias)
        if len(aliases) == 0:
            raise NameError("Alias does not exist")
        elif len(aliases) == 1 and aliases[0]['alias'] == alias:
            table_name = self.config_reader.get_value('table')
            alias_field = self.config_reader.get_value('where_field')
            query = "DELETE FROM %s WHERE %s = '%s'" % (table_name, alias_field, alias)
            cursor = self.dbc.cursor()
#            cursor.execute(query)
        else:
            raise NameError("Alias matched multiple records")            
        
    def insert_alias(self, alias='', dest='', overwrite=False):
        existing = self.get_aliases(alias=alias)
        if len(existing) == 0:
            table_name = self.config_reader.get_value('table')
            alias_field = self.config_reader.get_value('where_field')
            destination_field = self.config_reader.get_value('select_field')
                
            query = "INSERT INTO %s (%s, %s) VALUES ('%s', '%s')" \
            % (table_name, alias_field, destination_field, alias, dest)
            
            cursor = self.dbc.cursor()
#            cursor.execute(query)

        elif overwrite:
            self.delete_alias(alias)
            self.insert_alias(alias, dest, overwrite)
        else:
            raise NameError("Alias already exists!")
            
        
def options(parser):
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument("-s", "--show", action="store_const",
       const="show", dest="action", help=
            ("(default) List users. Username must be given"), default=True)
    mutex_group.add_argument("-i", "--insert", action="store_const", 
        const="insert", dest="action", help=("Insert user. "
            "A username must be given."))
    mutex_group.add_argument("--delete", action="store_const",
        const="delete", dest="action", help="Delete user.")
        
    params_group = parser.add_argument_group("Values")
    params_group.add_argument("-u", "--user", 
        dest="user", help="Username fragment")
    
    parser.set_defaults(action='show')
    opts = parser.parse_args()
    if opts.action == 'insert' and not (opts.user):
        parser.error(
        ("User name is required to add an alias.")
        )
    elif opts.action == 'delete' and not (opts.alias):
        parser.error(
            ("An alias must be specified.")
        )
    
    return opts
    
def main():
    opt = options(ArgumentParser())
    reader = Aliases()

    try:
        if opt.action == 'show':
            aliases = reader.get_aliases(alias = None, dest = None)
            for alias in aliases:
                print alias['email']
        elif opt.action == 'insert':
            aliases = reader.insert_alias(dest=opt.dest, alias=opt.alias)
        elif opt.action == 'delete':
            reader.delete_alias(alias=opt.alias)
    except PostfixConfig.NoPermissionException, exception:
        print "No permission to read %s" % exception.get_filename()
        
     
if __name__ == "__main__":
    main()
