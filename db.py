import pdb
import psycopg2
import bcrypt

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
    def __init__(self, dbName, dbUser, wordCount={}, tblName=None):
        Database.__init__(self, dbName, dbUser)
        self.word_count = wordCount
        if tblName:
            self.table_name = tblName

    def populate(self):
        self.create_cursor()
        for word, count in self.word_count.items():
            sql = 'INSERT INTO WordCount (word, count) VALUES (%s, %s);'
            try:
                self.cur.execute(sql, (word, count))
            except:
                print 'Could not insert {0}'.format(word)
                return
        self.commit_and_close()

    def increment_word(self, word):
        self.create_cursor()
        sql = 'UPDATE {0} SET count = count + 1 WHERE word = (%s);'.format(self.table_name)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not add 1 to {0}'s count".format(word)
        self.commit_and_close()

    def get_count(self, word):
        self.create_cursor()
        sql = 'SELECT count FROM {0} WHERE word = (%s);'.format(self.table_name)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not access {0} in {1}.".format(word, self.table_name)
        try:
            count = self.cur.fetchone()[0]
        except TypeError: # Word doesn't exist in table
            return
        self.commit_and_close()
        return count


class UserTable(Database):
    def __init__(self, dbName, dbUser, tableName):
        Database.__init__(self, dbName, dbUser)
        self.table = tableName

    def _check_username(self, username, password):
        sql = 'SELECT password FROM {0} WHERE username = (%s);'.format(self.table)
        try:
            self.cur.execute(sql, (username,))
        except:
            print "Couldn't access {0} from {1}.".format(username, self.table)

    def register(self, username, password):
        error = None
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.create_cursor()
        self._check_username(username, password)
        try:
            db_pass = self.cur.fetchone()[0]
        except TypeError:
            sql = 'INSERT INTO {0} (username, password) VALUES (%s, %s);'.format(self.table)
            self.cur.execute(sql, (username, password))
            self.commit_and_close()
        else:
            error = 'Username already registered'
        return error

    def login(self, username, password):
        error = None
        self.create_cursor()
        self._check_username(username, password)
        try:
            db_pass = self.cur.fetchone()[0]
        except TypeError:
            error = 'That username is not registered.'
        else:
            if db_pass != bcrypt.hashpw(password, db_pass):
                error = 'Your password does not match the password our records.'
        return error


class DBError(Exception): pass
