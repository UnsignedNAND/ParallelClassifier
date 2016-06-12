class Token(object):
    stem = None
    page_id = None
    count = 0
    freq = 0

    def __str__(self):
        return '{0:14} {1:4} {2:7}'.format(self.stem, self.count, self.freq)
