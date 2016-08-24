import multiprocessing

from core.utils import coord_2d_to_1d


class Clusterization(multiprocessing.Process):
    centers = {}

    def __init__(self, offset, shift, distances, parsed_docs, largest_id,
                 doc_class):
        super(self.__class__, self).__init__()
        self.offset = offset
        self.shift = shift  # how many elements should be skipped between iters
        self.distances = distances
        self.parsed_docs = parsed_docs
        self.largest_id = largest_id
        self.doc_class = doc_class

    def _receive_centers(self):
        pass

    def _find_closest_docs_to_center(self):
        pass

    def run(self):
        while True:
            self._receive_centers()
            if not self.centers:
                break
            self._find_closest_docs_to_center()
