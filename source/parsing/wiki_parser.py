import xml.sax

from data.db import Db
import multiprocessing
import time
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


class ProcessParser(multiprocessing.Process):
    def __init__(self, q_unparsed_documents):
        self._q_unparsed_documents = q_unparsed_documents
        super(self.__class__, self).__init__()

    def run(self):
        c = 0
        while True:
            # print(self._q_unparsed_documents.get())
            self._q_unparsed_documents.get()
            c += 1
            if self._q_unparsed_documents.empty():
                print(c)
                time.sleep(1)


class ProcessWriter(multiprocessing.Process):
    pass


@timer
def parse():
    # global session
    # session = Db.create_session()
    LOG.info("Started loading to database")

    q_unparsed_documents = multiprocessing.Queue()
    p_reader = ProcessReader(q_unparsed_documents)
    p_parser = ProcessParser(q_unparsed_documents)
    p_reader.start()
    p_parser.start()
    p_reader.join()
    p_parser.join()


if __name__ == '__main__':
    parse()
