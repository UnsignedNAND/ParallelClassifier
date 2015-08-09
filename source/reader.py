import xml.etree.ElementTree as etree
import os

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
        if self.xml_path is None:
            raise Exception('No source to parse!')

        articles_parsed = 0
        for event, elem in etree.iterparse(self.xml_path, events=('start', 'end', 'start-ns', 'end-ns')):
            if event == 'start' or str(elem).find('text') == -1:
                if event != 'start' and str(elem).find('title') != -1:
                    article_current = unicode(elem.text).encode('utf8')
                    print article_current
                    articles_parsed += 1
                    if articles_parsed >= 1:
                        break


if __name__ == '__main__':
    r = Reader('../data/wiki_dump.xml')
    r.parse_xml()
