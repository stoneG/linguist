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
    def __init__(self, dbName, dbUser, wordCount={}, tableName=None, FACTOR=280, MIN=20):
        Database.__init__(self, dbName, dbUser)
        self.word_count = wordCount
        if tableName:
            self.tbl = tableName
        self.score_zeroes = False
        self._get_total_words()
        self.size_factor = FACTOR
        self.min_size = MIN

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

    def _get_total_words(self):
        """Return the int count of all words in the WordCount table.
        Relies on the self.score_zeroes to determine if 0 frequency words
        are counted."""
        self.create_cursor()
        if self.score_zeroes:
            sql = 'SELECT count(word) FROM {0};'.format(self.tbl)
        else:
            sql = 'SELECT count(word) from {0} WHERE count>0;'.format(self.tbl)
        self.cur.execute(sql)
        total = self.cur.fetchone()[0]
        self.word_total = total

    def increment_word(self, word):
        self.create_cursor()
        sql = 'UPDATE {0} SET count = count + 1 WHERE word = (%s);'.format(self.tbl)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not add 1 to {0}'s count".format(word)
        self.commit_and_close()

    def get_count(self, word):
        self.create_cursor()
        sql = 'SELECT count FROM {0} WHERE word = (%s);'.format(self.tbl)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not access {0} in {1}.".format(word, self.tbl)
        try:
            count = self.cur.fetchone()[0]
        except TypeError: # Word doesn't exist in table
            return
        self.commit_and_close()
        return count

    def score(self, word, count):
        """Return the linguist score of the given word."""
        self.create_cursor()
        sql = 'SELECT count(word) FROM {0} WHERE count>{1}'.format(self.tbl, count)
        self.cur.execute(sql)
        rank = self.cur.fetchone()[0]
        percentile = rank/float(self.word_total)
        s = int(round(min(percentile*self.size_factor, self.size_factor))) + self.min_size
        self.commit_and_close()
        return s


class UserTable(Database):
    def __init__(self, dbName, dbUser, tableName):
        Database.__init__(self, dbName, dbUser)
        self.tbl = tableName

    def _check_username(self, username, password):
        sql = 'SELECT pwd FROM {0} WHERE uname = (%s);'.format(self.tbl)
        try:
            self.cur.execute(sql, (username,))
        except:
            print "Couldn't access {0} from {1}.".format(username, self.tbl)

    def register(self, username, password, fName, lName, email):
        error = None
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.create_cursor()
        self._check_username(username, password)
        try:
            db_pass = self.cur.fetchone()[0]
        except TypeError:
            sql =  'INSERT INTO ' + self.tbl + ' '
            sql += '(uname, pwd, fname, lname, email, words, scores) '
            sql += 'VALUES (%s, %s, %s, %s, %s, %s, %s);'
            self.cur.execute(sql, (username, password, fName, lName, email, '', ''))
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

    def add_to_word_score(self, username, word, score):
        sql = 'SELECT words, scores FROM {0} WHERE uname = (%s);'.format(self.tbl)
        self.create_cursor()
        self.cur.execute(sql, (username,))
        db_words, db_scores = self.cur.fetchone()
        db_words, db_scores = db_words.split(), db_scores.split()
        if word in db_words:
            raise ReuseError
        elif len(db_words) == 20:
            db_words = db_words[1:]
            db_scores = db_scores[1:]
        db_words.append(word)
        db_scores.append(str(score))
        db_words, db_scores = ' '.join(db_words), ' '.join(db_scores)
        sql =  'UPDATE {0} '.format(self.tbl)
        sql += 'SET words=(%s), scores=(%s) WHERE uname=(%s);'
        self.cur.execute(sql, (db_words, db_scores, username))
        self.commit_and_close()

    def get_user_info(self, username):
        sql =  'SELECT fname, lname, email, words, scores '
        sql += 'FROM {0} WHERE uname = (%s);'.format(self.tbl)
        self.create_cursor()
        self.cur.execute(sql, (username,))
        info = self.cur.fetchone()
        self.commit_and_close()
        return info


class DBError(Exception): pass
class ReuseError(Exception): pass
