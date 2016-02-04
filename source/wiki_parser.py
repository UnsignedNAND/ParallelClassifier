#!/usr/bin/python

import xml.sax
import logging

from db.db import Page, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('.', 'wiki_parser'))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

rootLogger.setLevel(logging.INFO)

engine = create_engine('sqlite:///db/sqlalchemy_example.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def write_page(title, text, redirect):
    page = Page()
    page.title = title
    page.text = text
    if redirect:
        page.redirect = redirect
        rootLogger.debug('Page redirect: ' + title + ' -> ' + redirect)

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
