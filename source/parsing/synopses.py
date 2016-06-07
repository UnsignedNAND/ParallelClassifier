# import numpy as np
# import pandas as pd
import nltk
import re
import os
import codecs
# import mpld3
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import SnowballStemmer
# from sklearn import feature_extraction


class Synopses:
    @staticmethod
    def _remove_stopwords(tokens):
        filtered_tokens = []
        stopwords = nltk.corpus.stopwords.words('english')
        for token in tokens:
            if token not in stopwords:
                filtered_tokens.append(token)
        return filtered_tokens


    @staticmethod
    def _remove_special_chars(text):
        text = re.sub(r'\W+', ' ', text).lower()
        return text

    @staticmethod
    def _trim_white_spaces(text):
        return " ".join(text.split())

    @staticmethod
    def _tokenize(text):
        tokens = [word for sent in nltk.sent_tokenize(text) for word in
                  nltk.word_tokenize(sent)]
        return tokens

    @staticmethod
    def _stemm(tokens):
        stemmer = SnowballStemmer("english")
        stems = [stemmer.stem(t) for t in tokens]
        return stems

    @staticmethod
    def make(text):
        text = Synopses._remove_special_chars(text)
        print('({0})_remove_special_chars:\t\t{1}'.format(len(text.split()),
                                                          text))

        text = Synopses._trim_white_spaces(text)
        print('({0})_trim_white_spaces:\t\t\t{1}'.format(len(text.split()),
                                                         text))

        text = Synopses._tokenize(text)
        print('({0}) _tokenize_:\t\t{1}'.format(len(text), text))

        text = Synopses._remove_stopwords(text)
        print('({0}) _remove_stopwords:\t\t{1}'.format(len(text), text))

        text = Synopses._stemm(text)
        print('({0}) _stemm:\t\t{1}'.format(len(text), text))

        print(Synopses._stemm(['network', 'networking']))
        return text

if __name__ == '__main__':
    from parsing.example_set import pages

    pages = pages
    pages = sorted(pages, key=lambda page: len(page.text))[:1]

    # for p in pages:
    #     print('{0} : {1}'.format(p.title, len(p.text)))
    for page in pages:
        Synopses.make(page.text)

    # ts = Synopses.make(text[:500])
    #
    # tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
    #                                    min_df=0.2, stop_words='english',
    #                                    use_idf=True,
    #                                    tokenizer=Synopses.make,
    #                                    ngram_range=(1, 3))
    #
    # # tfidf_matrix = tfidf_vectorizer.fit_transform(synopses)
    #
    # # print(tfidf_matrix.shape)
