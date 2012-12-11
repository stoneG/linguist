import re
import string
import time
import os

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


def current_time():
    return time.time()

OWLpath = 'wordlist/TWL06.txt'
textFolder = 'abc'
dic = {}
def main():
    global dic
    t = current_time()
    text_corpus = TextCorpus(textFolder, OWLpath)
    dic = text_corpus.build()
    print 'Program took %d seconds' % (current_time() - t)

if __name__ == '__main__':
    main()
