class Token(object):
    stem = None
    page_id = None
    count = 0
    tf = 0
    idf = 0.0  # because of formula, even if word does not exist in corpus it
    #  should have 1.0 value
    tf_idf = 0.0

    def __str__(self):
        return '{0:14} {1:4} {2:7} * {3:7} = {4:7}'.format(
            self.stem, self.count, self.tf, self.idf, self.tf_idf
        )

    def calc_tf_idf(self):
        self.tf_idf = self.idf * self.tf
        return self.tf_idf
