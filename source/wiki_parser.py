#!/usr/bin/python

import xml.sax
import logging
import os

from db.db import Page, Base, engine
from sqlalchemy.orm import sessionmaker


log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log_dir = '.'
log_file = "{1}.log".format(log_dir, str(__file__).split('.')[0])

logger = logging.getLogger()

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


class WikiContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.path = []
        self.text = None
        self.title = None
        self.redirect = None

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

    def characters(self, content):
        assert content is not None and len(content) > 0
        if len(self.path) == 0:
            return

        if self.path[-1] == "title":
            self.title += content
        elif self.path[-1] == "text":
            assert self.title is not None
            self.text += content

wiki_handler = WikiContentHandler()
sax_parser = xml.sax.make_parser()
sax_parser.setContentHandler(wiki_handler)

data_source = open('../data/wiki_dump.xml')
sax_parser.parse(data_source)
