import multiprocessing

from core.utils import coord_2d_to_1d


class Clusterization(multiprocessing.Process):

    def __init__(self, offset, shift, pipe_send_centers,
                 pipe_receive_centers, parsed_docs, distances, largest_id,
                 pipe_send_results):
        super(self.__class__, self).__init__()
        self.centers = {}
        self.offset = offset
        self.shift = shift
        self.pipe_send_centers = pipe_send_centers
        self.pipe_receive_centers = pipe_receive_centers
        self.parsed_docs = parsed_docs
        self.distances = distances
        self.largest_id = largest_id + 1
        self.pipe_send_results = pipe_send_results

    def _receive_centers(self):
        self.centers = self.pipe_receive_centers.recv()

    def _closest_center_id_for_doc_id(self, did):
        closest_cid = None
        closest_cid_distance = -100
        for cid in self.centers:
            cid_distance = self.distances[coord_2d_to_1d(cid, did,
                                                         self.largest_id)]
            if closest_cid_distance < cid_distance:
                closest_cid = cid
                closest_cid_distance = cid_distance
        if closest_cid is None:
            raise Exception('Error in finding closest '
                            'distance doc_id:{0}'.format(did))
        return closest_cid, closest_cid_distance

    def _find_closest_docs_to_center(self):
        did = self.offset
        while did < self.largest_id:
            closest_cid, distance = self._closest_center_id_for_doc_id(did)
            self.pipe_send_results.send({
                'cid': closest_cid,
                'did': did,
                'dist': distance,
            })
            did += self.shift
        self.pipe_send_results.send(None)

    def run(self):
        while True:
            self._receive_centers()
            if not self.centers:
                print(self.name, 'Received None')
                break
            self._find_closest_docs_to_center()
