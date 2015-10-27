import xml.etree.ElementTree as etree
import os
from models.article import Article


class Reader(object):
    xml_path = None

    def __init__(self, xml_path):
        self.load_xml(xml_path)

    def load_xml(self, xml_path):
        if os.path.exists(xml_path) and os.path.isfile(xml_path):
            self.xml_path = xml_path
        else:
            raise Exception('Either file does not exists or it is a directory')

    def parse_xml(self):
        articles_parsed = 0
        article_title = None
        article_category = None
        article_text = None

        for event, elem in etree.iterparse(self.xml_path, events=('start', 'end', 'start-ns', 'end-ns')):
            if event == 'start' or str(elem).find('text') == -1:
                if event != 'start' and str(elem).find('title') != -1:
                    article_title = unicode(elem.text).encode('utf8')
            else:
                article_category = 'Unknown'
                try:
                    article_category = unicode(elem.text).encode('utf8').split("Category:")[1]
                    article_category = article_category.split('|')[0]
                except Exception as ex:
                    pass
                article_text = unicode(elem.text).encode('utf8')

                article = Article()
                article.title = article_title
                article.wiki_category = article_category
                article.text = article_text
                article.print_short()
                articles_parsed += 1

                if articles_parsed > 5:
                    break


if __name__ == '__main__':
    r = Reader('../data/wiki_dump.xml')
    r.parse_xml()
