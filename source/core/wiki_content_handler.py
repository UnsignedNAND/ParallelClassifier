import math
import xml.sax

from data.db import Db, Models
from models.page import Page
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.general import str2bool
from utils.log import get_log

LOG = get_log()
CONF = get_conf()
session = None


class WikiContentHandler(xml.sax.ContentHandler):
    def __init__(self, q_unparsed_documents):
        self._path = []
        self._text = None
        self._title = None
        self._redirect = None
        self._items_limit = int(CONF['general']['item_limit'])
        self._classification_items_limit = int(
            CONF['classification']['item_limit'])
        self.items_saved = 0
        self._documents_saved = 0
        self._redirects_saved = 0
        self._q_unparsed_documents = q_unparsed_documents

        if str2bool(CONF['general']['save_to_db']):
            Db.init()
            Db.clean()  # database has to be cleaned every time to ensure
            # that IDs are unique
            self.session = Db.create_session()

    def startElement(self, name, attributes):
        if name == "page":
            assert self._path == []
            self._text = None
            self._title = None
            self._redirect = None
        elif name == "title":
            assert self._path == ["page"]
            assert self._title is None
            self._title = ""
        elif name == "redirect":
            assert self._path == ["page"]
            assert self._redirect is None
            self._redirect = attributes['title']
        elif name == "text":
            assert self._path == ["page"]
            assert self._text is None
            self._text = ""
        else:
            assert len(self._path) == 0 or self._path[-1] == "page"
            return

        self._path.append(name)

    def endElement(self, name):
        if len(self._path) > 0 and name == self._path[-1]:
            del self._path[-1]
        if name == "text":
            # We have the complete article: write it to db
            if not self._redirect:
                # Page
                page = Page()
                # reading is run in a single thread, so we can generate an
                # unique ID here
                page.id = self.items_saved
                page.content = self._text
                page.title = self._title
                self._q_unparsed_documents.put(page)

                if str2bool(CONF['general']['save_to_db']):
                    page = Models.Doc()
                    page.id = page.id = self.items_saved
                    page.text = self._text
                    page.title = self._title
                    self.session.add(page)
            else:
                pass
                # TODO do redirects carry any relevant information?
            self._monitor_progress()

    def _monitor_progress(self):
        self.items_saved += 1
        if not self._redirect:
            self._documents_saved += 1
        else:
            self._redirects_saved += 1

        if str2bool(CONF['general']['save_to_db']):
            if self.items_saved % 10:
                self.session.commit()

        if self.items_saved % (int(math.ceil(self._items_limit/10)) if int(
                math.ceil(self._items_limit/10)) > 0 else 1) == 0:
            LOG.debug('[{0:6.2f} %] Parsed {1} / {2} items'.format(
                self.items_saved / float(self._items_limit) * 100,
                self.items_saved, self._items_limit),
            )
        if self._items_limit and self.items_saved >= self._items_limit:
            if str2bool(CONF['general']['save_to_db']):
                self.session.commit()
            raise PageLimitException('Parser hit items limit ({0}), '
                                     'Parsed pages: {1}, '
                                     'Parsed redirects {2}'.format(
                                         self._items_limit,
                                         self._documents_saved,
                                         self._redirects_saved
                                         )
                                     )

    def characters(self, content):
        assert content is not None and len(content) > 0
        if len(self._path) == 0:
            return

        if self._path[-1] == "title":
            self._title += content
        elif self._path[-1] == "text":
            assert self._title is not None
            self._text += content
