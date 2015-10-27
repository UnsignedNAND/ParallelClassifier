class Article(object):
    title = ''
    text = ''
    wiki_category = ''

    def __init__(self):
        pass

    def print_short(self):
        self.remove_chars()
        print '%s : %s : %s' % (self.wiki_category, self.title, self.text[:80].replace('\n', ''))

    def remove_chars(self):
        chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[', ']', '{', '}', '|', '\\'
                 '/', '?', '>', '<', ',', '.']

        for char in chars:
            self.text = self.text.replace(char, ' ')
