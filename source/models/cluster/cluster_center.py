import math


class ClusterCenter(object):
    center_id = None
    doc_ids = {}
    avg_distance = 0.0
    center_changed = False
    previous_center_id = None
    pre_previous_center_id = None

    def __init__(self, cluster_center=None):
        if cluster_center:
            self.center_id = cluster_center.center_id
            self.doc_ids = cluster_center.doc_ids
            self.avg_distance = cluster_center.avg_distance
            self.center_changed = cluster_center.center_changed
            self.previous_center_id = cluster_center.previous_center_id
            self.pre_previous_center_id = cluster_center.pre_previous_center_id

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
        self.pre_previous_center_id = self.previous_center_id
        self.previous_center_id = self.center_id

        if len(self.doc_ids) == 1:
            return self.center_id

        for doc_id in self.doc_ids.keys():
            current_doc = self.doc_ids[doc_id]
            diff = math.fabs(current_doc['doc_center_distance'] - self.avg_distance)
            if 0.1 < diff <= closest_diff:
                closest_diff = diff
                closest_doc_id = doc_id

        # this is hack for avoiding endless loops
        if closest_doc_id == self.pre_previous_center_id:
            return closest_doc_id

        if self.previous_center_id != closest_doc_id:
            self.center_changed = True
            self.center_id = closest_doc_id
        return closest_doc_id
