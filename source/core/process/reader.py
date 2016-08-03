import multiprocessing
import xml.sax

from core.wiki_content_handler import WikiContentHandler
from utils.exceptions import PageLimitException
from utils.log import get_log

LOG = get_log()


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
