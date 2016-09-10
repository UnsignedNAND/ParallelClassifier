import multiprocessing

from sklearn import svm

class SVM(multiprocessing.Process):
    def __init__(self, pair_queue, result_queue, classes_doc, parsed_docs,
                 new_doc):
        super(self.__class__, self).__init__()
        self.pair_queue = pair_queue
        self.result_queue = result_queue
        self.current_pair = None
        self.classes_doc = classes_doc
        self.parsed_docs = parsed_docs
        self.new_doc = new_doc

    def _recv(self):
        val = self.pair_queue.get()
        if not val:
            self.result_queue.put(None)
            return None
        self.current_pair = val
        return val

    def _svm_pair(self):
        class1, class2 = self.current_pair

        class1_docs = self.classes_doc[class1]
        class2_docs = self.classes_doc[class2]
        all_docs = []
        all_docs.extend(class1_docs)
        all_docs.extend(class2_docs)

        tokens_template = {}
        class_distribution = []
        # create template for existing documents
        for doc_id in all_docs:
            doc = self.parsed_docs[doc_id]
            class_distribution.append(doc.center_id)
            for token in doc.tokens:
                tokens_template[token.stem] = 1

        for token in self.new_doc.tokens:
            tokens_template[token.stem] = 1
        tokens_template = list(tokens_template.keys())

        feature_matrix = []
        for doc_id in all_docs:
            feature_vector = []
            doc = self.parsed_docs[doc_id]
            for token in tokens_template:
                try:
                    feature_value = doc.tfidf[token]
                except:
                    feature_value = 0.0
                feature_vector.append(feature_value)
            feature_matrix.append(feature_vector)

        new_feature_vector = []
        for token in tokens_template:
            try:
                feature_value = self.new_doc.tfidf[token]
            except:
                feature_value = 0.0
            new_feature_vector.append(feature_value)

        class_distribution = [class1]*len(class1_docs)+[class2]*len(class2_docs)
        clf = svm.SVC(kernel='linear', C=1.0)
        clf.fit(feature_matrix, class_distribution)
        result = clf.predict(new_feature_vector)

        # send results
        self.result_queue.put({
            'class1': class1,
            'class2': class2,
            'result': result[0]
        })

    def run(self):
        while self._recv():
            self._svm_pair()
