def _lower_string(text):
    return text.lower()


def _remove_special_chars(text):
    special_chars = ". , : ; ( ) [ ] < > ? / \\ \" * $ = + - _ { } ! @ # % ^ & \n ! ' |"
    for char in special_chars.split():
        text = text.replace(char, ' ')
    return text


def _trim_white_spaces(text):
    return " ".join(text.split())


def _bag_of_words(text):
    # TODO test bow vs n-gram
    bow = {}
    for word in text.split():
        if word in bow.keys():
            bow[word] += 1
        else:
            bow[word] = 1
    return bow


def _filter(bow):
    words = len(bow)
    filtered = {}
    for word in bow.keys():
        if bow.get(word) > 1:
            filtered[word] = bow[word]
    return filtered


def simplify(text):
    text = _lower_string(text)
    text = _remove_special_chars(text)
    text = _trim_white_spaces(text)
    text = _bag_of_words(text)
    text = _filter(text)
    return text

if __name__ == '__main__':
    test = 'Hello world [!]   @test \n new line test  new new new world'
    print test
    print 20*'-'
    print simplify(test)
