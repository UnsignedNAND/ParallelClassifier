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
    def _remove_special_chars(text):
        """
        Method removes special characters from input. Returned string is
        alfa-numeric.
        """
        text = re.sub(r'\W+', ' ', text).lower()
        return text

    @staticmethod
    def _trim_white_spaces(text):
        return " ".join(text.split())

    @staticmethod
    def _stemm(tokens):
        # run stemmer and remove stop words
        stopwords = nltk.corpus.stopwords.words('english')
        stemmer = SnowballStemmer("english")
        tokens_total = 0
        counted_stems = {}
        for token in tokens:
            if token in stopwords:
                continue
            stemmed_token = stemmer.stem(token)
            tokens_total += 1
            if stemmed_token in counted_stems.keys():
                counted_stems[stemmed_token]['count'] += 1
            else:
                counted_stems[stemmed_token] = {
                    'count': 1
                }

        counted_stems['_meta'] = {
            'tokens_in_document': tokens_total
        }
        return counted_stems

    @staticmethod
    def _tf(tokens):
        """
        TF: Term Frequency, which measures how frequently a term occurs in a
        document. Since every document is different in length, it is possible
        that a term would appear much more times in long documents than shorter
        ones. Thus, the term frequency is often divided by the document length
        (aka. the total number of terms in the document) as a way of
        normalization:
        TF(t) = (Number of times term t appears in a document) / (Total
        number of terms in the document).
        """
        tokens_in_document = tokens['_meta']['tokens_in_document']
        for token in tokens.keys():
            if token == '_meta':
                continue
            tokens[token]['tf'] = tokens[token]['count'] / tokens_in_document
            print(tokens[token])
            # tokens[token]['tf'] = tokens[token]['tf']['count'] / \
            #                       tokens_in_document
        return tokens

    @staticmethod
    def make(text):
        text = Synopses._remove_special_chars(text)
        text = Synopses._trim_white_spaces(text)

        tokens = text.split()
        tokens = Synopses._stemm(tokens)
        tokens = Synopses._tf(tokens)

        from pprint import pprint
        pprint(tokens, indent=4)

        return text

if __name__ == '__main__':
    from parsing.example_set import pages

    pages = pages
    pages = sorted(pages, key=lambda page: len(page.text))[:1]

    for page in pages:
        Synopses.make(page.text)
