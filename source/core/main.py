import math
import multiprocessing

from collections import Counter
from core.process.classification import Classification
from core.process.clusterization import Clusterization
from core.process.distance import Distance
from core.process.idf import IDF
from core.process.parser import create_parsers
from core.process.reader import Reader
from core.utils import str_1d_as_2d, initialize_cluster_centers
from data.db import Db, Models
from models.page import Page
from utils.config import get_conf
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()
parsed_docs = {}
largest_id = -1
PROCESSES = int(CONF['general']['processes'])
distances = None
class_distances = None
tokens_idf = {}


def _receive_parsed_docs(queue_parsed_docs):
    global largest_id
    docs = {}
    processes_returned = 0
    while True:
        doc = queue_parsed_docs.get()
        if not doc:
            processes_returned += 1
            if processes_returned == PROCESSES:
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
    global tokens_idf

    # initialize communication

    queue_unparsed_docs = multiprocessing.Queue()
    queue_parsed_docs = multiprocessing.Queue()
    pipe_tokens_to_idf_parent, pipe_tokens_to_idf_child = multiprocessing.Pipe()
    pipes_tokens_to_processes_parent = []
    pipes_tokens_to_processes_child = []
    for i in range(PROCESSES):
        pipe_tokens_to_processes_parent, pipe_tokens_to_processes_child = \
            multiprocessing.Pipe()
        pipes_tokens_to_processes_parent.append(pipe_tokens_to_processes_parent)
        pipes_tokens_to_processes_child.append(pipe_tokens_to_processes_child)

    # additional pipe to transfer IDF values from IDF process to master
    pipe_idf_master_parent, pipe_idf_master_child = multiprocessing.Pipe()
    pipes_tokens_to_processes_parent.append(pipe_idf_master_parent)

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
        process_num=PROCESSES
    )
    ps_idf = IDF(
        pipe_tokens_to_idf_parent=pipe_tokens_to_idf_parent,
        docs_num=int(CONF['general']['item_limit']),
        event=event,
        pipes_tokens_to_processes_parent=pipes_tokens_to_processes_parent,
        process_num=PROCESSES
    )

    # read all the articles from XML and do TF-IDF
    ps_reader.start()

    LOG.info("Started processing documents using {0} processes".format(
        PROCESSES))
    for ps_parser in ps_parsers:
        ps_parser.start()
    ps_idf.start()

    # receive tokens IDF values from IDF process
    tokens_idf = pipe_idf_master_child.recv()

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
        PROCESSES)
    )
    distances = multiprocessing.Array('d', (largest_id+1)*(largest_id+1))

    dist_ps = []
    for i in range(PROCESSES):
        dist_p = Distance(
            iteration_offset=i,
            iteration_size=PROCESSES,
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
    LOG.info('Starting clusterization using {0} processes'.format(PROCESSES))

    center_num = int(CONF['clusterization']['centers'])
    centers = initialize_cluster_centers(
        center_num=center_num,
        start=0,
        end=largest_id,
        parsed_docs=parsed_docs
    )
    LOG.debug('Generated initial centers: {0}'.format(len(centers)))
    LOG.debug('Centers are documents with IDs: {0}'
              .format(sorted(list(centers.keys()))))

    cluster_ps = []
    pipe_receive_results, pipe_send_results = multiprocessing.Pipe()

    for pid in range(PROCESSES):
        pipe_send_centers, pipe_receive_centers = multiprocessing.Pipe()
        cluster_p = Clusterization(
            offset=pid,
            shift=PROCESSES,
            pipe_send_centers=pipe_send_centers,
            pipe_receive_centers=pipe_receive_centers,
            parsed_docs=parsed_docs,
            distances=distances,
            largest_id=largest_id,
            pipe_send_results=pipe_send_results,
        )
        cluster_p.start()
        cluster_p.pipe_send_centers.send(list(centers.keys()))
        cluster_ps.append(cluster_p)

    iteration = 0
    iteration_limit = int(CONF['clusterization']['iterations_limit'])
    while iteration < iteration_limit:
        not_finished = PROCESSES
        while not_finished:
            recv = pipe_receive_results.recv()
            if not recv:
                not_finished -= 1
            else:
                cid = recv['cid']
                did = recv['did']
                dist = recv['dist']
                centers[cid].add_doc(doc_id=did, distance=dist)

        for cid in centers:
            print(centers[cid])
        # if there was change - send new centers and move to another iter
        iteration += 1
    LOG.debug('Finished after {0} iteration(s)'.format(iteration))

    for cluster_p in cluster_ps:
        cluster_p.pipe_send_centers.send(None)
        cluster_p.join()

    # pipe_results_parent, pipe_results_child = multiprocessing.Pipe()
    # cluster_ps = []
    # pipes_centers = []
    #
    # LOG.debug('Starting with centers: {0}'.format(sorted(centers.keys())))
    #
    # for i in range(process_num):
    #     pipe_centers_parent, pipe_centers_child = multiprocessing.Pipe()
    #     pipes_centers.append((pipe_centers_parent, pipe_centers_child))
    #     cluster_p = Clusterization(
    #         pipe_results_child=pipe_results_child,
    #         iteration_offset=i,
    #         iteration_size=process_num,
    #         distances=distances,
    #         pipe_centers_child=pipe_centers_child,
    #         largest_id=largest_id
    #     )
    #     cluster_p.start()
    #     cluster_ps.append(cluster_p)
    #
    # changes = int(CONF['clusterization']['centers'])  # 1st ending condition
    # iterations = 0
    # while changes:
    #     if int(CONF['clusterization']['iterations_limit']) <= iterations:
    #         LOG.info('Clusterization hit iterations hard limit ({0})'.format(
    #             CONF['clusterization']['iterations_limit']
    #         ))
    #         break
    #     iterations += 1
    #     LOG.debug('{0} Iteration {1} {2}'.format('-'*10, iterations, '-'*10))
    #     changes = int(CONF['clusterization']['centers'])
    #     not_finished = process_num
    #     new_centers = {}
    #     for (pipe_center_parent,_) in pipes_centers:
    #         pipe_center_parent.send(centers)
    #
    #     while not_finished:
    #         recv = pipe_results_parent.recv()
    #         if not recv:
    #             not_finished -= 1
    #         else:
    #             centers[recv['closest_center_id']].add_doc(
    #                 doc_id=recv['doc_id'],
    #                 distance=recv['distance']
    #             )
    #     new_centers = {}
    #     for cid in centers:
    #         center = centers[cid]
    #         LOG.debug(str(center))
    #         center.find_closest_doc_to_average()
    #         if not center.center_changed:
    #             changes -= 1
    #         LOG.debug('{0} Closest to avg: {1} '.format(
    #             center.center_changed,
    #             center.center_id
    #         ))
    #         # moving documents assigned to this center to backup list so they
    #         # do not get lost if this is the last iteration
    #         center.pre_doc_ids = centers[cid].doc_ids
    #         center.doc_ids = {}
    #         new_centers[center.center_id] = center
    #     centers = new_centers
    #
    # for cid in centers.keys():
    #     center = centers[cid]
    #     msg = '\nCenter: {1} [{0}]'.format(
    #         center.center_id,
    #         parsed_docs[center.center_id].title
    #     )
    #     for did in center.pre_doc_ids:
    #         parsed_docs[did].center_id = center.center_id
    #         msg += '\n{0} - {1}'.format(did, parsed_docs[did].title)
    #     LOG.debug(msg)
    #
    # for (pipe_center_parent, _) in pipes_centers:
    #     # send pills to processes
    #     pipe_center_parent.send(None)
    #
    # for cluster_p in cluster_ps:
    #     cluster_p.join()
    # LOG.info('Finished clusterization in {0} iterations'.format(iterations))


@timer
def _prepare_new_doc(doc):
    page = Page()
    page.title = doc.title
    page.content = doc.text
    page.create_tokens()
    # import tokens IDF values from already classified documents
    # TODO check if multiprocessing would be of any benefit
    for page_token in page.tokens:
        try:
            # TODO increment total number of docs by 1
            page_token.idf = tokens_idf[page_token.stem]
        except KeyError:
            # token did not appear in previous documents
            page_token.idf = 1 + math.log((len(parsed_docs) + 1) / 1.0,
                                          math.e)
            LOG.debug('Classification: token \'{0}\' is new.'.format(
                page_token.stem))
        finally:
            page.calc_tokens_tfidf()
    return page


@timer
def classify():
    Db.init()
    session = Db.create_session()
    docs = session.query(Models.Doc).filter(
        Models.Doc.id == int(CONF['classification']['new_doc_start_id'])
    )
    if docs.count():
        for doc in docs:
            LOG.info('Classifying "{0}"'.format(doc.title))
            new_doc = _prepare_new_doc(doc)
            class_distances = multiprocessing.Array('d', (largest_id + 1))
            class_ps = []
            for i in range(PROCESSES):
                class_p = Classification(
                    iteration_offset=i,
                    iteration_size=PROCESSES,
                    class_distances=class_distances,
                    largest_id=largest_id,
                    parsed_docs=parsed_docs,
                    new_doc=new_doc,
                )
                class_p.start()
                class_ps.append(class_p)

            for class_p in class_ps:
                class_p.join()

            id_dist = []
            for i in range(largest_id + 1):
                try:
                    item = {
                        'id': i,
                        'distance': class_distances[i],
                        'class': parsed_docs[i].center_id
                    }
                    id_dist.append(item)
                except KeyError:
                    pass

            # finding most frequent center in close neighborhood
            id_dist.sort(key=lambda x: x['distance'], reverse=True)
            k_id_dist = id_dist[:int(CONF['classification']['k'])]
            classes = [c['class'] for c in k_id_dist]
            counted_classes = Counter(classes)
            new_doc.center_id, _ = counted_classes.most_common(1)[0]
            LOG.info('New doc ({0}) classified as belonging to {1} : {2}'.
                     format(new_doc.title, new_doc.center_id,
                     parsed_docs[new_doc.center_id].title))

    else:
        LOG.info('No documents to classify')


if __name__ == '__main__':
    parse()
    distance()
    cluster()
    classify()
