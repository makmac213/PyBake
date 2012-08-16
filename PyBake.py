import MySQLdb

INDENT = "    "

class MyException(Exception):
    def requiredKeys(self, args):
        message = 'Please specify '
        missingKey = ''
        if 'engine' not in args:
            missingKey = 'engine '
        if 'hostname' not in args:
            missingKey = 'hostname '
        if 'user' not in args:
            missingKey = 'user '
        if 'password' not in args:
            missingKey = 'password '
        if not missingKey == '':
            raise MyException(message+missingKey)
        
class PyBake:
    CONFIG = {}
    db = ''
    schema = ''
    myException = MyException()
    tables = []
    QUERIES = {
        'mysql': {
            'getTables': """SELECT DISTINCT(table_name)
                            FROM columns
                            WHERE table_schema = '%s'""",
            'getColumns': """SELECT
                                column_name, is_nullable, data_type, character_maximum_length,
                                column_default, column_key, extra, column_type
                             FROM columns
                             WHERE table_schema = '%s'
                                AND table_name = '%s'""",
        }
    }
    
    def __init__(self, schema, **kwargs):
        self.schema = schema
        if len(kwargs)>0:
            self.setConfig(kwargs)

    def connect(self, **kwargs):
        if len(kwargs)>0:
            self.setConfig(kwargs)
        try:
            self.myException.requiredKeys(self.CONFIG)
            if self.CONFIG['engine'] == 'mysql':
                self.db = MySQLdb.connect(self.CONFIG['hostname'],
                                     self.CONFIG['user'],
                                     self.CONFIG['password'],
                                     'information_schema')                
        except MyException, e:
            print e

    def getTables(self):
        if self.db == '':
            print 'Please connect to the database. '
        else:
            sql = self.QUERIES['mysql']['getTables'] % (self.schema)
            cursor = self.db.cursor()
            try:
                cursor.execute(sql)
                for row in cursor.fetchall():
                    self.tables.append(row[0])
            except:
                print 'May nag error habang kinukuha ang mga lamesa'
            #print self.tables

    def getTableColumns(self, table):
        results = []
        if self.db == '':
            print 'Please connect to the database. '
        else:
            sql = self.QUERIES['mysql']['getColumns'] % (self.schema, table)
            cursor = self.db.cursor()
            try:
                cursor.execute(sql)
                return cursor.fetchall()
                #print row[self.QUERIES['mysql']['column_name']]
            except:
                print 'May nag error habang kinukuha ang mga columns. '

    def createModel(self):
        p.getTables()
        print 
        for table in self.tables:
            print 'class %s(models.Model):' % (table.title())
            for tableRow in self.getTableColumns(table):
                    print INDENT + tableRow[0],
                    
                    if tableRow[0] == 'id':
                        if tableRow[6] == 'auto_increment':
                            print '= models.AutoField()'
                        else:
                            print '= models.IntegerField()'
                    elif tableRow[2] in ('varchar','char', 'nvarchar', 'nchar'):
                        print '= models.CharField(max_length=%d)' % (tableRow[3])
                    elif tableRow[2] in ('text','ntext','mediumtext'):
                        print '= models.TextField()'
                    elif tableRow[2] in ('date'):
                        opts = ''
                        if tableRow[4] in ('0000-00-00 00:00:00', 'CURRENT_TIMESTAMP'):
                            opts = opts + 'auto_now_add=True,'                        
                        print '= models.DateField(%s)' % opts                       
                    elif tableRow[2] in ('datetime', 'timestamp'):
                        opts = ''
                        if tableRow[4] in ('0000-00-00 00:00:00', 'CURRENT_TIMESTAMP'):
                            opts = opts + 'auto_now_add=True,'                        
                        print '= models.DateTimeField(%s)' % opts
                    elif tableRow[2] in ('int'):
                        print '= models.IntegerField()'
                    elif tableRow[2] in ('enum'):
                        # EnumField
                        # http://stackoverflow.com/questions/21454/specifying-a-mysql-enum-in-a-django-model
                        opts = 'values='+tableRow[7][4:]
                        print '= models.EnumField(%s)' % opts
                    else:
                        print ''
            print ''
                
                
    def setConfig(self, kwargs):
        for key in kwargs.keys():
            self.CONFIG[key] = kwargs[key]


if __name__ == "__main__":
    p = PyBake('cq',hostname='localhost', user='root', password='pass123', engine='mysql')
    p.connect()
    p.createModel()
