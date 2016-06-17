class Token(object):
    stem = None
    page_id = None
    count = 0
    freq = 0
    idf = 1.0  # because of formula, even if word does not exist in corpus it
    #  should have 1.0 value

    def __str__(self):
        return '{0:14} {1:4} {2:7}'.format(self.stem, self.count, self.freq)
