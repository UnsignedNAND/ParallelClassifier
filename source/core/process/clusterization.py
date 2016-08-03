import multiprocessing

from core.utils import coord_2d_to_1d


class Clusterization(multiprocessing.Process):
    centers = {}

    def __init__(self, pipe_results_child, iteration_offset, iteration_size,
                 distances, pipe_centers_child, largest_id):
        self.iteration_offset = iteration_offset
        self.iteration_size = iteration_size
        self.distances = distances
        self.pipe_results_child = pipe_results_child
        self.pipe_centers_child = pipe_centers_child
        self.largest_id = largest_id
        super(self.__class__, self).__init__()

    def _receive_centers(self):
        self.centers = self.pipe_centers_child.recv()

    def _find_closest_docs_to_center(self):
        doc_id = self.iteration_offset
        while doc_id < (self.largest_id + 1):
            if self.distances[doc_id] >= 0:
                closest_center = None
                closest_center_distance = None
                for center_id in self.centers:
                    center_distance = self.distances[
                        coord_2d_to_1d(center_id, doc_id, self.largest_id + 1)
                    ]
                    if closest_center_distance is None or \
                                    closest_center_distance < center_distance:
                        closest_center_distance = center_distance
                        closest_center = center_id
                self.pipe_results_child.send(
                    {
                        'doc_id': doc_id,
                        'closest_center_id': closest_center,
                        'distance': closest_center_distance,
                    }
                )
            doc_id += self.iteration_size
        self.pipe_results_child.send(None)

    def run(self):
        while True:
            self._receive_centers()
            if not self.centers:
                break
            self._find_closest_docs_to_center()