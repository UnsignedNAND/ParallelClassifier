import math
import xml.sax

from data.db import Db, Models
from sqlalchemy.exc import DataError
from utils.config import get_conf
from utils.exceptions import PageLimitException
from utils.log import get_log
from utils.timer import timer

CONF = get_conf()
LOG = get_log()


class WikiContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self._path = []
        self._text = None
        self._title = None
        self._redirect = None
        self._pages_limit = int(CONF['dev']['item_limit'])
        self.items_saved = 0
        self._pages_saved = 0
        self._redirects_saved = 0

    def _save_element(self, **kwargs):
        session = Db.create_session()
        element = None

        if kwargs['type'] is None:
            LOG.error('Unknown element type: ' + kwargs['type'])
        if kwargs['type'] == 'page':
            element = Models.Page()
            element.title = kwargs['title']
            element.text = kwargs['text']

        try:
            session.add(element)
            session.commit()
        except DataError:
            LOG.critical('Data too long to store: ' + str(len(element.text)))
            exit()

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
                self._pages_saved += 1
                self._save_element(type='page', title=self._title,
                                   text=self._text)
            else:
                self._redirects_saved += 1
                # write_redirect(title=self.title, target=self.redirect)

            self.items_saved += 1
            if self.items_saved % (int(math.ceil(self._pages_limit/10))
                                    if int(math.ceil(self._pages_limit/10)) > 0
                                    else 1) == 0:
                LOG.debug('[{0:6.2f} %] Parsed {1} / {2} items'.format(
                    self.items_saved / float(self._pages_limit) * 100,
                    self.items_saved, self._pages_limit),
                )
            if self._pages_limit and self.items_saved >= self._pages_limit:
                raise PageLimitException('Parser hit items limit ({0}), '
                                         'Parsed pages: {1}, '
                                         'Parsed redirects {2}'.format(
                                             self._pages_limit,
                                             self._pages_saved,
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


@timer
def parse():
    LOG.info("Started loading to database")
    wiki_handler = WikiContentHandler()
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

if __name__ == '__main__':
    parse()
