import nltk
import re

from utils.config import get_conf
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()
STOPWORDS = nltk.corpus.stopwords.words('english')
STEMMER = nltk.stem.snowball.SnowballStemmer("english")


def _remove_special_chars(string):
    """
    Method removes special characters from input. Returned string is
    alfa-numeric.
    """
    clear_string = re.sub(r'\W+', ' ', string).lower()
    return clear_string


def _trim_white_spaces(text):
    return " ".join(text.split())


def _tf(tokens, tokens_in_document=1):
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
    def _limit_decimal_points(num):
        return int((num*10000)) / 10000.0

    for token in tokens.keys():
        if token == '_meta':
            continue
        tf = tokens[token]['count'] / tokens_in_document
        tf = _limit_decimal_points(tf)
        tokens[token]['tf'] = tf
    return tokens


def _clean(tokens):
    ctokens = {}
    for token in tokens:
        if token in STOPWORDS:
            continue
        stemmed_token = STEMMER.stem(token)
        if stemmed_token in ctokens.keys():
            ctokens[stemmed_token]['count'] += 1
        else:
            ctokens[stemmed_token] = {
                'count': 1
            }
    return ctokens


def parse(text):
    """
    :param text: String
    :return: Dict
    'stemmed-token': {'count': <how-man-times-token-appears-in-doc>,
                      'tf': <token-frequency-in-doc>}
    """
    text = _remove_special_chars(text)
    text = _trim_white_spaces(text)
    tokens = text.split()
    total_words = len(tokens)
    clean_tokens = _clean(tokens)
    counted_tokens = _tf(clean_tokens, total_words)

    return counted_tokens

if __name__ == '__main__':
    from multiprocessing import Process, Queue
    from parsing.example_set import pages
    qin = Queue()
    qout = Queue()

    for page in pages:
        qin.put(page)

    @timer
    def test():
        def process_parsing(pid, qin, qout):
            while not qin.empty():
                d = qin.get()
                parse(d.text)
                print(pid, ': parsed:', d.title)

        ps = []
        for i in range(0, 4):
            ps.append(Process(target=process_parsing, args=(i, qin, qout)))

        for p in ps:
            p.start()

        for p in ps:
            p.join()

    test()
