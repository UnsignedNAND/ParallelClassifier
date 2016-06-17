import xml.sax

import multiprocessing
from parsing.wiki_content_handler import WikiContentHandler
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()


class Process(object):
    class Reader(multiprocessing.Process):
        def __init__(self, q_unparsed_documents):
            self._q_unparsed_documents = q_unparsed_documents
            super(self.__class__, self).__init__()

        def run(self):
            wiki_handler = WikiContentHandler(self._q_unparsed_documents)
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
                self._q_unparsed_documents.put(None)

    class Parser(multiprocessing.Process):
        def __init__(self, q_unparsed_documents, p_idf_child, event):
            self._q_unparsed_documents = q_unparsed_documents
            self.p_idf_child = p_idf_child
            self.event = event
            super(self.__class__, self).__init__()

        def run(self):
            parsed_docs = 0
            while True:
                page = self._q_unparsed_documents.get()
                if page is None:
                    # Just to be sure that other threads can also take a pill
                    self._q_unparsed_documents.put(None)
                    self.p_idf_child.send(None)
                    print('Process {0} finished after parsing {1} '
                          'docs'.format(self.pid, parsed_docs))
                    break
                page.create_tokens()
                for token in page.tokens:
                    self.p_idf_child.send(token.stem)
                page.content_clean()
                parsed_docs += 1
            print('Process {0} waiting on IDF to finish...'.format(self.pid))
            self.event.wait()
            print('Process {0} finished waiting on IDF...'.format(
                self.pid))

    class IDF(multiprocessing.Process):
        def __init__(self, p_idf_parent, num_docs, event):
            self.p_idf_parent = p_idf_parent  # parent pipe for IDF
            self.num_docs = num_docs  # total number of documents
            self.event = event
            self.tokens = {}
            super(self.__class__, self).__init__()

        def run(self):
            pills = 0
            while pills < 4:
                msg = self.p_idf_parent.recv()
                if msg is None:
                    pills += 1
                    continue
                if msg in self.tokens.keys():
                    self.tokens[msg] += 1
                else:
                    self.tokens[msg] = 1

            for token in self.tokens:
                # IDF(token) = 1 + log_e(Total Number Of Documents / Number Of
                # Documents with token in it)
                import math
                token_idf = 1 + math.log(self.num_docs / self.tokens[token],
                                         math.e)
                self.tokens[token] = token_idf
            self.event.set()

    @staticmethod
    def create_parsers(**kwargs):
        processes = []
        for i in range(0, kwargs['num_of_processes']):
            process = Process.Parser(
                q_unparsed_documents=kwargs['q_unparsed_documents'],
                p_idf_child=kwargs['p_idf_child'],
                event=kwargs['event']
            )
            processes.append(process)
        return processes


@timer
def parse():
    LOG.info("Started loading to database")

    q_unparsed_documents = multiprocessing.Queue()
    p_idf_parent, p_idf_child = multiprocessing.Pipe()
    event = multiprocessing.Event()
    event.clear()

    ps_reader = Process.Reader(q_unparsed_documents=q_unparsed_documents)
    ps_parsers = Process.create_parsers(
        num_of_processes=int(CONF['general']['processes']),
        q_unparsed_documents=q_unparsed_documents,
        p_idf_child=p_idf_child,
        event=event
    )
    ps_idf = Process.IDF(
        p_idf_parent=p_idf_parent,
        num_docs=int(CONF['general']['processes']),
        event=event
    )

    ps_reader.start()

    LOG.debug('Spawning {0} parser processes'.format(int(CONF['general'][
                                                         'processes'])))
    for ps_parser in ps_parsers:
        ps_parser.start()
    ps_idf.start()

    ps_reader.join()
    for ps_parser in ps_parsers:
        ps_parser.join()


if __name__ == '__main__':
    parse()
