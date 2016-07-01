import nltk
import re

from models.token import Token

STOPWORDS = nltk.corpus.stopwords.words('english')
STEMMER = nltk.stem.snowball.SnowballStemmer("english")


class Page(object):
    id = None
    title = None
    content = None
    tokens = []
    word_count = None  # Word count in original text

    def number_of_tokens(self):
        return len(self.tokens)

    def content_clean(self):
        del self.content

    def create_tokens(self):
        self.tokens = []
        self.word_count = 0
        # remote special characters
        self.content = re.sub(r'\W+', ' ', self.content).lower()

        words = self.content.split()
        self.word_count = len(words)

        temp_words = {}
        for word in words:
            if word in STOPWORDS:
                continue
            # to make sure we only count really relative words
            self.word_count += 1
            stem = STEMMER.stem(word)
            if stem in temp_words.keys():
                temp_words[stem] += 1
            else:
                temp_words[stem] = 1

        for stem in temp_words.keys():
            token = Token()
            token.stem = stem
            token.count = temp_words[stem]
            token.tf = int((token.count / self.word_count * 100000)) / \
                       100000.0
            self.tokens.append(token)

    def __str__(self):
        text = self.title
        for token in self.tokens:
            text += '\n\t{0}'.format(token)
        text += '\nTokens total: {0} Unique tokens: {1}'.format(
            self.word_count, len(self.tokens))
        return text

    def top_tokens(self, num=5):
        return list(sorted(
            self.tokens,
            reverse=True,
            key=lambda token: token.tf_idf
        ))[:num]
