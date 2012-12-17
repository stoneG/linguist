import pdb
import psycopg2

class Database(object):
    def __init__(self, dbName, dbUser):
        """Param : Description
        dbName   : Str name of the database to connect to
        dbUser   : Str name of the psql user
        wordCount: Dict of word counts
        """
        self.db_name = dbName
        self.user = dbUser

    def create_cursor(self):
        name_and_user = "dbname={0} user={1}".format(self.db_name, self.user)
        self.conn = psycopg2.connect(name_and_user)
        self.cur = self.conn.cursor()

    def commit_and_close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create(self, tblName, colAndType):
        """Create table in database.
        parameter  : description
        tblName    : str name of table to create
        colAndType : list of col name and type, where the first entry is the primary key
                     ie [colA_name, colA_type, colBname, colBtype, etc...]
        """
        self.create_cursor()
        create = 'CREATE TABLE {0} '.format(tblName)
        structure = '({0} {1} PRIMARY KEY'.format(colAndType[0], colAndType[1])
        for i in range(2, len(colAndType), 2):
            structure += ', {0} {1}'.format(colAndType[i], colAndType[i+1])
        sql = create + structure + ');'
        try:
            self.cur.execute(sql)
        except:
            print 'Table could not be created'
            print 'Statement was:\n{0}'.format(sql)
            raise DBError
        self.table_name = tblName
        self.commit_and_close()


class WordCountTable(Database):
    def __init__(self, dbName, dbUser, wordCount):
        Database.__init__(self, dbName, dbUser)
        self.word_count = wordCount
        self.populated = False

    def populate(self):
        self.create_cursor()
        for word, count in self.word_count.items():
            sql = 'INSERT INTO WordCount (word, count) VALUES (%s, %s);'
            try:
                self.cur.execute(sql, (word, count))
            except:
                print 'Could not insert {0}'.format(word)
                return
        self.populated = True
        self.commit_and_close()

    def increment_word(self, word):
        self.create_cursor()
        sql = 'UPDATE {0} SET count = count + 1 WHERE word = (%s)'.format(self.table_name)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not add 1 to {0}'s count".format(word)
        self.commit_and_close()

    def get_count(self, word):
        if not self.populated:
            print 'Populate table first please'
            raise DBError
        self.create_cursor()
        sql = 'SELECT count FROM {0} WHERE word = (%s)'.format(self.table_name)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not access {0} in {1}.".format(word, self.table_name)
        count = self.cur.fetchone()[0]
        return count


class UserTable(Database):
    def __init__(self, dbName, dbUser, wordCount):
        Database.__init__(self, dbName, dbUser, wordCount)


class DBError(Exception): pass
