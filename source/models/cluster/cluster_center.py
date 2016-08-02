class ClusterCenter(object):
    center_id = None
    doc_ids = {}
    avg_distance = 0.0

    def add_doc(self, doc_id, doc_center_distance):
        self.doc_ids[doc_id] = doc_id
        self.avg_distance += (doc_center_distance-self.avg_distance)/len(
            self.doc_ids)

    def __str__(self):
        return 'cid: {0} avg: {1} doc_ids: {2}'.format(self.center_id,
                                                       self.avg_distance,
                                                       [self.doc_ids[did] for
                                                        did in
                                                        self.doc_ids.keys()])
