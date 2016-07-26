import multiprocessing
import numpy
import timeit
import xml.sax

from parsing.utils import calc_distance
from parsing.wiki_content_handler import WikiContentHandler
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()
parsed_docs = {}
largest_id = -1


class Process(object):
    class Reader(multiprocessing.Process):
        def __init__(self, q_unparsed_docs):
            self._q_unparsed_docs = q_unparsed_docs
            super(self.__class__, self).__init__()

        def run(self):
            wiki_handler = WikiContentHandler(self._q_unparsed_docs)
            sax_parser = xml.sax.make_parser()
            sax_parser.setContentHandler(wiki_handler)

            try:
                data_source = open('../data/wiki_dump.xml')
                sax_parser.parse(data_source)
                LOG.info('Parsed {0} items'.format(wiki_handler.items_saved))
            except PageLimitException as page_limit_exception:
                LOG.info(page_limit_exception)
            except KeyboardInterrupt:
                exit()
            finally:
                # A pill for other threads
                self._q_unparsed_docs.put(None)

    class Parser(multiprocessing.Process):
        def __init__(self, queue_unparsed_docs, pipe_tokens_to_idf_child,
                     event, pipe_tokens_to_processes_child, queue_parsed_docs):
            self._queue_unparsed_docs = queue_unparsed_docs
            self._pipe_tokens_to_idf_child = pipe_tokens_to_idf_child
            self._event = event
            self._pipe_tokens_to_processes_child = \
                pipe_tokens_to_processes_child
            self._queue_parsed_docs = queue_parsed_docs
            super(self.__class__, self).__init__()

        def run(self):
            parsed_pages_num = 0
            parsed_pages = []
            while True:
                page = self._queue_unparsed_docs.get()
                if page is None:
                    # Just to be sure that other threads can also take a pill
                    self._queue_unparsed_docs.put(None)
                    self._pipe_tokens_to_idf_child.send(None)
                    print('Process {0} finished after parsing {1} '
                          'docs'.format(self.pid, parsed_pages_num))
                    break
                page.create_tokens()
                for token in page.tokens:
                    self._pipe_tokens_to_idf_child.send(token.stem)
                page.content_clean()
                parsed_pages_num += 1
                parsed_pages.append(page)

            print('Process {0} waiting on IDF to finish...'.format(self.pid))
            self._event.wait()
            recv_tokens = self._pipe_tokens_to_processes_child.recv()
            print('Process {0} received {1} tokens from IDF'.format(
                self.pid, len(recv_tokens)))
            for page in parsed_pages:
                for token in page.tokens:
                    try:
                        token.idf = recv_tokens[token.stem]
                        token.calc_tf_idf()
                    except KeyError as ke:
                        print('error', token)
                self._queue_parsed_docs.put(page)
            # sending process-end pill
            self._queue_parsed_docs.put(None)

    class IDF(multiprocessing.Process):
        def __init__(self, pipe_tokens_to_idf_parent, docs_num, event,
                     pipes_tokens_to_processes_parent):
            self._pipe_tokens_to_idf_parent = pipe_tokens_to_idf_parent
            self._docs_num = docs_num  # total number of documents
            self._event = event
            self._tokens = {}
            self._pipes_tokens_to_processes_parent = \
                pipes_tokens_to_processes_parent
            super(self.__class__, self).__init__()

        def run(self):
            pills = 0
            while pills < 4:
                msg = self._pipe_tokens_to_idf_parent.recv()
                if msg is None:
                    pills += 1
                    continue
                if msg in self._tokens.keys():
                    self._tokens[msg] += 1
                else:
                    self._tokens[msg] = 1

            for token in self._tokens:
                # IDF(token) = 1 + log_e(Total Number Of Documents / Number Of
                # Documents with token in it)
                import math
                token_idf = 1 + math.log(self._docs_num / self._tokens[token],
                                         math.e)
                self._tokens[token] = token_idf

            self._event.set()
            for pipe in self._pipes_tokens_to_processes_parent:
                pipe.send(self._tokens)
            print('IDF sent {0} tokens'.format(len(self._tokens)))

    class Distance(multiprocessing.Process):
        def __init__(self, iteration_offset, iteration_size, pipe):
            """
            This process calculates distance between documents.
            :param iteration_offset: offset by which the iteration will be
            started.
            :param iteration_size: usually should be equal to the number of
            processes working on the same data. Incrementing data cell by
            this value will ensure that each process is working without any
            collisions.
            """
            self.iteration_offset = iteration_offset
            self.iteration_size = iteration_size
            self.pipe = pipe
            super(self.__class__, self).__init__()

        def run(self):
            x = self.iteration_offset
            while x < largest_id+1:
                if x not in parsed_docs.keys():
                    self.pipe.send((x, x, -1.0))
                    x += self.iteration_size
                    continue
                doc1 = parsed_docs[x]
                for y in range(x+1):
                    dist = -1.0
                    if y in parsed_docs.keys():
                        doc2 = parsed_docs[y]
                        dist = calc_distance(doc1, doc2)
                    self.pipe.send((x, y, dist))
                x += self.iteration_size
            self.pipe.send((None, None, None))

    @staticmethod
    def create_parsers(process_num, queue_unparsed_documents,
                       pipe_tokens_to_idf_child, event,
                       pipes_tokens_to_processes_child, queue_parsed_docs):
        processes = []
        for i in range(process_num):
            process = Process.Parser(
                queue_unparsed_docs=queue_unparsed_documents,
                pipe_tokens_to_idf_child=pipe_tokens_to_idf_child,
                event=event,
                pipe_tokens_to_processes_child
                =pipes_tokens_to_processes_child[i],
                queue_parsed_docs=queue_parsed_docs
            )
            processes.append(process)
        return processes


def _receive_parsed_docs(process_num, queue_parsed_docs):
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
    LOG.info("Started loading to database")
    process_num = int(CONF['general']['processes'])

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

    ps_reader = Process.Reader(q_unparsed_docs=queue_unparsed_docs)
    ps_parsers = Process.create_parsers(
        process_num=process_num,
        queue_unparsed_documents=queue_unparsed_docs,
        pipe_tokens_to_idf_child=pipe_tokens_to_idf_child,
        event=event,
        pipes_tokens_to_processes_child=pipes_tokens_to_processes_child,
        queue_parsed_docs=queue_parsed_docs
    )
    ps_idf = Process.IDF(
        pipe_tokens_to_idf_parent=pipe_tokens_to_idf_parent,
        docs_num=int(CONF['dev']['item_limit']),
        event=event,
        pipes_tokens_to_processes_parent=pipes_tokens_to_processes_parent
    )

    # read all the articles from XML and do TF-IDF
    ps_reader.start()

    LOG.debug('Spawning {0} parser processes'.format(process_num))
    for ps_parser in ps_parsers:
        ps_parser.start()
    ps_idf.start()

    ps_reader.join()
    ps_idf.join()

    # processes will not end until all the data is not received
    parsed_docs = _receive_parsed_docs(process_num, queue_parsed_docs)

    for ps_parser in ps_parsers:
        ps_parser.join()

    # count distances to avoid counting distances twice we measure it only
        # once for each pair of documents

    time_distance_start = timeit.default_timer()
    distances = numpy.zeros((largest_id+1, largest_id+1))
    pipe_dist_parent, pipe_dist_child = multiprocessing.Pipe()

    dist_ps = []
    for i in range(process_num):
        dist_p = Process.Distance(i, process_num, pipe_dist_child)
        dist_p.start()
        dist_ps.append(dist_p)

    kill = process_num
    while kill:
        (x, y, dist) = pipe_dist_parent.recv()
        print((x,y,dist))
        if not dist:
            kill -= 1
            continue
        distances[x][y] = dist
        distances[y][x] = dist

    for dist_p in dist_ps:
        dist_p.join()
    time_distance_end = timeit.default_timer()
    time_distance_delta = time_distance_end - time_distance_start

    for doc_id in parsed_docs:
        print(parsed_docs[doc_id].title)
        for doc_id2 in parsed_docs:
            print('\t', distances[parsed_docs[doc_id].id][parsed_docs[
                doc_id2].id],
                  parsed_docs[doc_id2].title)
    print(time_distance_delta)

if __name__ == '__main__':
    parse()
