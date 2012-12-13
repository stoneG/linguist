
class Database(object):
    def __init__(self, dbName, dbUser, wordCount):
        """Param : Description
        dbName   : Str name of the database to connect to
        dbUser   : Str name of the psql user
        wordCount: Dict of word counts
        """
        self.name = dbName
        self.user = dbUser
        self.word_count = wordCount

    def create_cursor(self):
        name_and_user = "dbname={0} user={1}".format(self.name, self.user)
        self.conn = psycopg2.connect(name_and_user)
        self.cur = self.conn.cursor()

    def commit_and_close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_table(self, name):
        """Create WordCount table in database."""
        self.create_cursor()
        sql = 'CREATE TABLE {0} (word varchar PRIMARY KEY, count integer);'.format(name)
        try:
            self.cur.execute(sql)
        except:
            print 'Table could not be created'
            return
        for word, count in self.word_count.items():
            sql = 'INSERT INTO {0} (word, count) VALUES (%s, %s);'.format(name)
            try:
                self.cur.execute(sql, (word, count))
            except:
                print 'Could not insert {0}'.format(word)
                return
        self.commit_and_close()

    def add_word(self, word):
        self.create_cursor()
        sql = 'UPDATE {0} SET count = count + 1 WHERE word = (%s)'.format(name)
        try:
            self.cur.execute(sql, (word,))
        except:
            print "Could not add 1 to {0}'s count".format(word)
        self.commit_and_close()
