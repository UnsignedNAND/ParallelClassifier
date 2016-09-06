import multiprocessing


class SVM(multiprocessing.Process):
    def __init__(self, pair_queue, result_queue):
        super(self.__class__, self).__init__()
        self.pair_queue = pair_queue
        self.result_queue = result_queue
        self.current_pair = None

    def _recv(self):
        val = self.pair_queue.get()
        if not val:
            self.result_queue.put(None)
            return None
        self.current_pair = val
        return val

    def _svm_pair(self):
        class1, class2 = self.current_pair
        result = None

        # send results
        self.result_queue.put({
            'class1': class1,
            'class2': class2,
            'result': result
        })

    def run(self):
        print(self.pid, 'started')
        while self._recv():
            self._svm_pair()
        print(self.pid, 'finished')


def _create_matrix_template(parsed_docs, k_closest, new_doc):
    tokens_template = {}  # feature matrix header
    matrix = []

    # add tokens from existing documents
    for did in k_closest:
        # create key-vector for feature matrix
        for token in parsed_docs[did['id']].tokens:
            tokens_template[token.stem] = 1

    # add tokens from new document
    for token in new_doc.tokens:
        tokens_template[token.stem] = 1

    tokens_template = list(tokens_template.keys())
    return tokens_template


def create_feature_matrix(k_closest, parsed_docs, new_doc):
    tokens_template = _create_matrix_template()
    matrix = {}
    for did in k_closest:
        doc = parsed_docs[did['id']]
        doc_feature = []
        for token in tokens_template:
            feature_value = 0.0
            try:
                feature_value = doc.tfidf[token]
            except:
                pass
            doc_feature.append(feature_value)
        matrix[did] = doc_feature

    doc_feature = []
    for token in tokens_template:
        feature_value = 0.0
        try:
            feature_value = new_doc.tfidf[token]
        except:
            pass
        doc_feature.append(feature_value)
    # new doc is saved under special '-1' key
    matrix[-1] = doc_feature
    return matrix
