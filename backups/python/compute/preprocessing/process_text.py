import re

from utils.config_manager import get_conf

conf = get_conf()


def _lower_string(text):
    return text.lower()


def _remove_special_chars(text):
    text = re.sub(r'\W+', ' ', text)
    return text


def _trim_white_spaces(text):
    return " ".join(text.split())


def _bag_of_words(text):
    # TODO test BoW vs n-gram
    bow = {}
    for word in text.split():
        if word in bow.keys():
            bow[word]['count'] += 1
        else:
            bow[word] = {
                'count': 1
            }

    # normalizing the dictionary
    length = float(len(bow))
    for word in bow.keys():
        bow[word]['normalized'] = bow[word]['count'] / length
    return bow


def _filter(bow):
    filtered = {}
    for word in bow.keys():
        if bow[word]['normalized'] > float(conf['process'][
                                               'normalize_minimal']):
            filtered[word] = bow[word]
    return filtered


def simplify(text, filtering=True):
    text = _lower_string(text)
    text = _remove_special_chars(text)
    text = _trim_white_spaces(text)
    text = _bag_of_words(text)
    if filtering:
        text = _filter(text)
    return text

if __name__ == '__main__':
    test = 'Hello world [!]   @test \n new line test  new new new world'
    print test
    print 20*'-'
    print simplify(test)
