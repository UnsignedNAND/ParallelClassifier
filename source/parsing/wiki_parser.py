import xml.sax

import multiprocessing
from parsing.text_parser import parse as text_parse
from parsing.wiki_content_handler import WikiContentHandler
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()


class ProcessReader(multiprocessing.Process):
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


class ProcessParser(multiprocessing.Process):
    def __init__(self, q_unparsed_documents):
        self._q_unparsed_documents = q_unparsed_documents
        super(self.__class__, self).__init__()

    def run(self):
        c = 0
        while True:
            text = self._q_unparsed_documents.get()
            if text is None:
                # Just to be sure that other threads can also take a pill
                self._q_unparsed_documents.put(None)
                print(multiprocessing.current_process().pid, c)
                return
            text_parse(text)
            if c % 100 == 0:
                print('progress', multiprocessing.current_process().pid, c)
            c += 1


def create_process_parser(**kwargs):
    processes = []
    for i in range(0, kwargs['num_of_processes']):
        process = ProcessParser(kwargs['q_unparsed_documents'])
        process.start()
        processes.append(process)
    return processes

@timer
def parse():
    # global session
    # session = Db.create_session()
    LOG.info("Started loading to database")

    q_unparsed_documents = multiprocessing.Queue()
    p_reader = ProcessReader(q_unparsed_documents)
    p_reader.start()

    LOG.debug('Spawning {0} parser processes'.format(int(CONF['general'][
                                                         'processes'])))
    ps_parser = create_process_parser(
        num_of_processes=int(CONF['general']['processes']),
        q_unparsed_documents=q_unparsed_documents
    )

    p_reader.join()
    for p_parser in ps_parser:
        p_parser.join()


if __name__ == '__main__':
    parse()
