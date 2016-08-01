class ClusterCenter(object):
    center_id = None
    doc_ids = {}
    avg_distance = 0.0

    def add_doc(self, doc_id, doc_center_distance):
        self.doc_ids[doc_id] = doc_center_distance
