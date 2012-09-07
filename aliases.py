#!/usr/bin/python

import ConfigParser
import PostfixConfig
from argparse import ArgumentParser
import MySQLdb, MySQLdb.cursors

class Aliases:
    def __init__(self):    
        self.dbc = None

    def get_dbc(self):
        self.config = ConfigParser.SafeConfigParser()

        self.config.read('config.ini')
        aliases_file = self.config.get('Postfix Config', 'alias_file')
        self.config_reader = PostfixConfig.Reader(aliases_file)
    
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
        alias_field = self.config_reader.get_value('where_field')
        destination_field = self.config_reader.get_value('select_field')

        query = "SELECT %s AS alias, %s AS destination FROM %s " \
        % (alias_field, destination_field, table_name)
        
        if alias or dest:
            query += "WHERE "
            if alias and len(alias) > 0:
                query += "%s LIKE '%%%s%%' " % (alias_field, alias)
            if alias and dest:
                query += "AND "
            if dest and len(dest) > 0:
                query += "%s LIKE '%%%s%%' " % (destination_field, dest)
        query += "ORDER BY %s ASC" % (alias_field)
        
        print query
        cursor = self.dbc.cursor()
        cursor.execute(query)
        alias_list = cursor.fetchall()
        return alias_list
        
    def set_alias(self, alias='', dest='', overwrite=False):
        existing = self.get_aliases(alias=alias)
        if len(existing) == 0:
            table_name = self.config_reader.get_value('table')
            alias_field = self.config_reader.get_value('where_field')
            destination_field = self.config_reader.get_value('select_field')
                
            query = "INSERT INTO %s (%s, %s) VALUES (%s, %s)" \
            % (table_name, alias_field, destination_field, alias, dest)
            
            print query
        elif overwrite:
            return
        else:
            print "Alias already exists!"
            
        
def options(parser):
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument("-s", "--show", action="store_const",
       const="show", dest="action", help=
            ("(default) List aliases. Alias and/or destination may be given"
            "but are optional."), default=True)
    mutex_group.add_argument("-i", "--insert", action="store_const", 
        const="insert", dest="action", help=("Insert alias. "
            "An alias and its destination must be given."))
        
    params_group = parser.add_argument_group("Values")
    params_group.add_argument("-a", "--alias", 
        dest="alias", help="Alias fragment.")
    params_group.add_argument("-d", "--destination",
        dest="dest", help="Destination fragment")
    
    parser.set_defaults(action='show')
    opts = parser.parse_args()
    if opts.action == 'insert' and not (opts.alias and opts.dest):
        parser.error(
        ("Alias and destination are required to add an alias.")
        )
    
    return opts
    
def main():
    opt = options(ArgumentParser())
    reader = Aliases()
    
    try:
        if opt.action == 'show':
            aliases = reader.get_aliases(alias = opt.alias, dest=opt.dest)
            for alias in aliases:
                print alias['alias'], alias['destination']
        elif opt.action == 'insert':
            aliases = reader.set_alias(dest=opt.dest, alias=opt.alias)
    except PostfixConfig.NoPermissionException, exception:
        print "No permission to read %s" %exception.get_filename()
        
     
if __name__ == "__main__":
    main()
