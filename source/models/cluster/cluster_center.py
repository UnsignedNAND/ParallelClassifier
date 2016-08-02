import math


class ClusterCenter(object):
    center_id = None
    doc_ids = {}
    avg_distance = 0.0
    center_changed = False
    previous_center_id = None

    def add_doc(self, doc_id, doc_center_distance):
        self.doc_ids[doc_id] = {
            'doc_id': doc_id,
            'doc_center_distance': doc_center_distance,  # distance to the
            # closest center
        }
        self.avg_distance += (doc_center_distance-self.avg_distance)/len(
            self.doc_ids)

    def __str__(self):
        return 'cid: {0} avg: {1} doc_ids: {2}'.format(self.center_id,
                                                       self.avg_distance,
                                                       [self.doc_ids[did] for
                                                        did in
                                                        self.doc_ids.keys()])

    def find_closest_doc_to_average(self):
        """
        This method looks for doc which distance is closest to the avg of
        distances between documents and the center. Found document is
        proposed as a new center of a group.
        Returns:

        """
        closest_diff = 9999
        closest_doc_id = None
        self.center_changed = False
        self.previous_center_id = self.center_id

        for doc_id in self.doc_ids.keys():
            current_doc = self.doc_ids[doc_id]
            diff = math.fabs(current_doc['doc_center_distance'] - self.avg_distance)
            if diff < closest_diff:
                closest_diff = diff
                closest_doc_id = doc_id

        if self.previous_center_id != closest_doc_id:
            self.center_changed = True
            self.center_id = closest_doc_id
        return closest_doc_id
