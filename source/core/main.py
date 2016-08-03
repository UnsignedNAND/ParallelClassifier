import logging
import multiprocessing

from core.process.reader import Reader
from core.process.parser import create_parsers
from core.process.idf import IDF
from core.process.distance import Distance
from core.utils import coord_2d_to_1d, str_1d_as_2d, \
    initialize_cluster_centers
from utils.config import get_conf
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()
parsed_docs = {}
largest_id = -1
process_num = int(CONF['general']['processes'])
distances = None


class Process(object):

    class Clusterization(multiprocessing.Process):
        centers = {}

        def __init__(self, pipe_results_child, iteration_offset, iteration_size,
                     distances, pipe_centers_child):
            self.iteration_offset = iteration_offset
            self.iteration_size = iteration_size
            self.distances = distances
            self.pipe_results_child = pipe_results_child
            self.pipe_centers_child = pipe_centers_child
            super(self.__class__, self).__init__()

        def _receive_centers(self):
            self.centers = self.pipe_centers_child.recv()

        def _find_closest_docs_to_center(self):
            doc_id = self.iteration_offset
            while doc_id < (largest_id + 1):
                if self.distances[doc_id] >= 0:
                    closest_center = None
                    closest_center_distance = None
                    for center_id in self.centers:
                        center_distance = distances[
                            coord_2d_to_1d(center_id, doc_id, largest_id + 1)
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


def _receive_parsed_docs(queue_parsed_docs):
    global largest_id
    docs = {}
    processes_returned = 0
    while True:
        doc = queue_parsed_docs.get()
        if not doc:
            processes_returned += 1
            if processes_returned == process_num:
                break
        else:
            docs[doc.id] = doc
            if largest_id < doc.id:
                largest_id = doc.id
    LOG.debug('Received {0} parsed docs.'.format(len(docs)))
    return docs


@timer
def parse():
    global parsed_docs
    global largest_id

    # initialize communication

    queue_unparsed_docs = multiprocessing.Queue()
    queue_parsed_docs = multiprocessing.Queue()
    pipe_tokens_to_idf_parent, pipe_tokens_to_idf_child = multiprocessing.Pipe()
    pipes_tokens_to_processes_parent = []
    pipes_tokens_to_processes_child = []
    for i in range(process_num):
        pipe_tokens_to_processes_parent, pipe_tokens_to_processes_child = \
            multiprocessing.Pipe()
        pipes_tokens_to_processes_parent.append(pipe_tokens_to_processes_parent)
        pipes_tokens_to_processes_child.append(pipe_tokens_to_processes_child)
    event = multiprocessing.Event()
    event.clear()

    # set up processes

    ps_reader = Reader(q_unparsed_docs=queue_unparsed_docs)
    ps_parsers = create_parsers(
        queue_unparsed_documents=queue_unparsed_docs,
        pipe_tokens_to_idf_child=pipe_tokens_to_idf_child,
        event=event,
        pipes_tokens_to_processes_child=pipes_tokens_to_processes_child,
        queue_parsed_docs=queue_parsed_docs,
        process_num=process_num
    )
    ps_idf = IDF(
        pipe_tokens_to_idf_parent=pipe_tokens_to_idf_parent,
        docs_num=int(CONF['dev']['item_limit']),
        event=event,
        pipes_tokens_to_processes_parent=pipes_tokens_to_processes_parent,
        process_num=process_num
    )

    # read all the articles from XML and do TF-IDF
    ps_reader.start()

    LOG.info("Started core documents using {0} processes".format(process_num))
    for ps_parser in ps_parsers:
        ps_parser.start()
    ps_idf.start()

    ps_reader.join()
    ps_idf.join()

    # processes will not end until all the data is not received
    parsed_docs = _receive_parsed_docs(queue_parsed_docs)

    for ps_parser in ps_parsers:
        ps_parser.join()


@timer
def distance():
    global distances
    LOG.info('Starting calculating distance using {0} processes'.format(
        process_num)
    )
    distances = multiprocessing.Array('d', (largest_id+1)*(largest_id+1))

    dist_ps = []
    for i in range(process_num):
        dist_p = Distance(
            iteration_offset=i,
            iteration_size=process_num,
            distances=distances,
            largest_id=largest_id,
            parsed_docs=parsed_docs
        )
        dist_p.start()
        dist_ps.append(dist_p)

    for dist_p in dist_ps:
        dist_p.join()

    LOG.debug('Distances: \n' + str_1d_as_2d(distances, largest_id+1))
    LOG.info('Done calculating distance for {0} documents'.format(
        len(parsed_docs)))


@timer
def cluster():
    global distances
    LOG.info('Starting clusterization using {0} processes'.format(process_num))

    center_num = int(CONF['clusterization']['centers'])
    centers = initialize_cluster_centers(
        center_num=center_num,
        start=0,
        end=largest_id,
        docs_num=len(parsed_docs),
        distances=distances
    )
    pipe_results_parent, pipe_results_child = multiprocessing.Pipe()
    cluster_ps = []
    pipes_centers = []

    LOG.debug('Starting with centers: {0}'.format(sorted(centers.keys())))

    for i in range(process_num):
        pipe_centers_parent, pipe_centers_child = multiprocessing.Pipe()
        pipes_centers.append((pipe_centers_parent, pipe_centers_child))
        cluster_p = Process.Clusterization(
            pipe_results_child=pipe_results_child,
            iteration_offset=i,
            iteration_size=process_num,
            distances=distances,
            pipe_centers_child=pipe_centers_child,
        )
        cluster_p.start()
        cluster_ps.append(cluster_p)

    changes = int(CONF['clusterization']['centers'])  # 1st ending condition
    iterations = 0
    while changes:
        if int(CONF['clusterization']['iterations_limit']) <= iterations:
            LOG.info('Clusterization hit iterations hard limit ({0})'.format(
                CONF['clusterization']['iterations_limit']
            ))
            break
        iterations += 1
        LOG.debug('{0} Iteration {1} {2}'.format('-'*10, iterations, '-'*10))
        changes = int(CONF['clusterization']['centers'])
        not_finished = process_num
        new_centers = {}
        for (pipe_center_parent,_) in pipes_centers:
            pipe_center_parent.send(centers)

        while not_finished:
            recv = pipe_results_parent.recv()
            if not recv:
                not_finished -= 1
            else:
                centers[recv['closest_center_id']].add_doc(
                    doc_id=recv['doc_id'],
                    distance=recv['distance']
                )
        new_centers = {}
        for cid in centers:
            center = centers[cid]
            LOG.debug(str(center))
            center.find_closest_doc_to_average()
            if not center.center_changed:
                changes -= 1
            LOG.debug('{0} Closest to avg: {1} '.format(
                center.center_changed,
                center.center_id
            ))
            # moving documents assigned to this center to backup list so they
            # do not get lost if this is the last iteration
            center.pre_doc_ids = centers[cid].doc_ids
            center.doc_ids = {}
            new_centers[center.center_id] = center
        centers = new_centers

    if LOG.level is logging.DEBUG:
        for cid in centers.keys():
            center = centers[cid]
            msg = '\nCenter: {1} [{0}]'.format(
                center.center_id,
                parsed_docs[center.center_id].title
            )
            for did in center.pre_doc_ids:
                msg += '\n{0} - {1}'.format(did, parsed_docs[did].title)
            LOG.debug(msg)

    for (pipe_center_parent, _) in pipes_centers:
        # send pills to processes
        pipe_center_parent.send(None)

    for cluster_p in cluster_ps:
        cluster_p.join()
    LOG.info('Finished clusterization in {0} iterations'.format(iterations))


if __name__ == '__main__':
    parse()
    distance()
    cluster()
