import multiprocessing

from core.utils import calc_distance


class Classification(multiprocessing.Process):
    def __init__(self, iteration_offset, iteration_size, class_distances,
                 largest_id, parsed_docs, new_doc):
        self.iteration_offset = iteration_offset
        self.iteration_size = iteration_size
        self.class_distances = class_distances
        self.largest_id = largest_id
        self.parsed_docs = parsed_docs
        self.new_doc = new_doc
        super(self.__class__, self).__init__()

    def run(self):
        doc_id = self.iteration_offset
        while doc_id < (self.largest_id + 1):
            try:
                existing_doc = self.parsed_docs[doc_id]
                distance = calc_distance(self.new_doc, existing_doc)
                self.class_distances[doc_id] = distance
            except:
                # there is no document with such ID, distance is -1
                self.class_distances[doc_id] = -1

            doc_id += self.iteration_size
