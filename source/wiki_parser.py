#!/usr/bin/python

import xml.sax
import logging

from db.db import Page, Base, engine
from sqlalchemy.orm import sessionmaker

from utils.timer import timer


log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log_file = "{0}.log".format(str(__file__).split('.')[0])

logger = logging.getLogger('wiki_parser')

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)

Base.metadata.bind = engine
db_session = sessionmaker(bind=engine)
session = db_session()


def write_page(title, text, redirect):
    page = Page()
    page.title = title
    page.text = text
    if redirect:
        page.redirect = redirect
        logger.debug('Page redirect: ' + title + ' -> ' + redirect)

    session.add(page)
    session.commit()


class PageLimitException(Exception):
    pass


class WikiContentHandler(xml.sax.ContentHandler):
    def __init__(self, pages_limit=None):
        self.path = []
        self.text = None
        self.title = None
        self.redirect = None
        self.pages_limit = pages_limit
        self.pages_saved = 0

    def startElement(self, name, attributes):
        if name == "page":
            assert self.path == []
            self.text = None
            self.title = None
            self.redirect = None
        elif name == "title":
            assert self.path == ["page"]
            assert self.title is None
            self.title = ""
        elif name == "redirect":
            assert self.path == ["page"]
            assert self.redirect is None
            self.redirect = attributes['title']
        elif name == "text":
            assert self.path == ["page"]
            assert self.text is None
            self.text = ""
        else:
            assert len(self.path) == 0 or self.path[-1] == "page"
            return

        self.path.append(name)

    def endElement(self, name):
        if len(self.path) > 0 and name == self.path[-1]:
            del self.path[-1]
        if name == "text":
            # We have the complete article: write it out
            write_page(self.title, self.text, self.redirect)
            self.pages_saved += 1
            if self.pages_limit and self.pages_saved >= self.pages_limit:
                raise PageLimitException("Parser hit pages limit ({0})".format(self.pages_limit))

    def characters(self, content):
        assert content is not None and len(content) > 0
        if len(self.path) == 0:
            return

        if self.path[-1] == "title":
            self.title += content
        elif self.path[-1] == "text":
            assert self.title is not None
            self.text += content


@timer
def main():
    wiki_handler = WikiContentHandler(pages_limit=None)
    sax_parser = xml.sax.make_parser()
    sax_parser.setContentHandler(wiki_handler)

    try:
        data_source = open('../data/wiki_dump.xml')
        sax_parser.parse(data_source)
    except PageLimitException as page_limit_exception:
        logger.info(page_limit_exception.message)

if __name__ == '__main__':
    main()
