#!/usr/bin/python

import ConfigParser
import ConfigReader
from optparse import OptionParser, OptionGroup
import MySQLdb, MySQLdb.cursors

class Aliases:
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()

        self.config.read('config.ini')
        self.aliases_file = self.config.get('Postfix Config', 'alias_file')
    
        user = ConfigReader.get_value(self.aliases_file, 'user')
        #host deliberately excluded - use localhost or go home
        password = ConfigReader.get_value(self.aliases_file, 'password')
        db_name = ConfigReader.get_value(self.aliases_file, 'dbname')
    
        self.dbc = MySQLdb.connect(
            user = user, passwd = password, db = db_name, 
            cursorclass=MySQLdb.cursors.DictCursor)    
    
    
    def get_aliases(self, alias='', dest=''):
        table_name = ConfigReader.get_value(self.aliases_file, 'table')
        alias_field = ConfigReader.get_value(self.aliases_file, 'where_field')
        destination_field = ConfigReader.get_value(
            self.aliases_file, 'select_field')

        query = "SELECT %s AS alias, %s AS destination FROM %s " \
        % (alias_field, destination_field, table_name)
        
        if alias or dest:
            query += "WHERE "
            if alias and len(alias) > 0:
                query += "%s LIKE '%%%s%%' " % (alias_field, alias)
            if dest and len(dest) > 0:
                query += "%s LIKE '%%%s%%' " % (destination_field, dest)
        query += "ORDER BY %s ASC" % (alias_field)
        
        cursor = self.dbc.cursor()
        cursor.execute(query)
        alias_list = cursor.fetchall()
        return alias_list
        
def options(option_parser):
    option_parser.add_option("--show", action="store_true", 
        dest="show", help=
        """List aliases. Alias and/or destination may be given 
        but are optional.""", default=True)
    option_parser.add_option("-i", "--insert", action="store_true", 
        dest="insert", help="""Insert alias. 
        An alias and its destination must be given.""")
        
    params_group = OptionGroup(option_parser, "Values")
    params_group.add_option("-a", "--alias", 
        dest="alias", help="Alias fragment.")
    params_group.add_option("-d", "--destination",
        dest="dest", help="Destination fragment")
    option_parser.add_option_group(params_group)
    
    (opts, args) = option_parser.parse_args()
    if opts.insert and not (opts.alias and opts.dest):
        option_parser.error("""
        Alias and destination are required to add an alias."""
        )
    
    return opts
    
def main():
    opt = options(OptionParser())
    reader = Aliases()
    
    if opt.show:
        aliases = reader.get_aliases(opt.alias, opt.dest)
        for alias in aliases:
            print alias['alias'], alias['destination']
        
     
if __name__ == "__main__":
    main()
