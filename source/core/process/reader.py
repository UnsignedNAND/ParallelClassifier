import multiprocessing
import xml.sax

from core.wiki_content_handler import WikiContentHandler
from data.db import Db, Models
from models.page import Page
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.general import str2bool
from utils.log import get_log

LOG = get_log()
CONF = get_conf()


class Reader(multiprocessing.Process):
    def __init__(self, q_unparsed_docs):
        self._q_unparsed_docs = q_unparsed_docs
        super(self.__class__, self).__init__()

    def _read_from_file(self):
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

    def _read_from_db(self):
        Db.init()
        session = Db.create_session()
        pages = session.query(Models.Page).all()
        for page in pages:
            p = Page()
            p.id = page.id
            p.title = page.title
            p.content = page.text
            self._q_unparsed_docs.put(p)
        self._q_unparsed_docs.put(None)

    def run(self):
        if str2bool(CONF['general']['load_from_db']):
            LOG.info('Loading from DB')
            self._read_from_db()
        else:
            self._read_from_file()
