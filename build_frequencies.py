import re
import string
import time
import os

import psycopg2

# Database: linguist

# Construct OWL dictionary
class OfficialWords(object):
    def __init__(self, OWLpath):
        OWL = open(OWLpath, 'r')
        self.list = [word.strip(' \t\n\r').lower() for word in OWL if len(word) > 4]
        OWL.close()
        self.dict = dict(zip(self.list,[0]*len(self.list)))

    def update(self, word, freq):
        """Increments word in self.dict if it exists."""
        try:
            self.dict[word] = freq
        except KeyError:
            pass

# Construct word counts for OWL words
# os.listdir('.') for cwd files
# os.getcwd() to get cwd path
# os.chdir('folder') to change the cwd to /folder.
# os.chdir('..') to move up the cwd level
class TextCorpus(object):
    def __init__(self, textFolder, OWLpath):
        self.OWL = OfficialWords(OWLpath)
        os.chdir(textFolder)
        self.file_names = os.listdir('.')

    def build(self):
        for index, name in enumerate(self.file_names):
            text = Text(name)
            for word, count in text.get_word_and_count():
                if len(word) <= 4:
                    continue
                else:
                    self.OWL.update(word, int(count))
            print index+1, 'files built'
        return(self.OWL.dict)

    def parent_directory(self):
        os.chdir('..')


class Text(object):
    def __init__(self, file_name):
        f = open(file_name, 'r')
        self.string = f.read()
        self.word_pat = re.compile(ur'\[\[([\w]+)\]\]\s+\|\|\s+(\d+)')
        f.close()

    def get_word_and_count(self):
        """Return a tuple of word and that word's count."""
        match = re.findall(self.word_pat, self.string)
        return match

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
        self.conn = psycopg2.connection(name_and_user)
        self.cur = self.conn.cursor()

    def commit_and_close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_table(self):
        """Create WordCount table in database."""
        name = 'WordCount'
        self.create_cursor()
        sql = 'CREATE TABLE {0} (word varchar PRIMARY KEY, count integer);'.format(name)
        self.cur.execute(sql)
        for word, count in self.word_count.items():
            sql = 'INSERT INTO {0} (word, count) VALUES (%s, %s);'.format(name)
            self.cur.execute(sql, (word, count))
        self.commit_and_close()


OWLpath = 'wordlist/TWL06.txt'
textFolder = 'abc'
dic = {}
def main():
    global dic
    text_corpus = TextCorpus(textFolder, OWLpath)
    dic = text_corpus.build()

if __name__ == '__main__':
    main()
