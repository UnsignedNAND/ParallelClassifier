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
        articles_parsed = 0
        for event, elem in etree.iterparse(self.xml_path, events=('start', 'end', 'start-ns', 'end-ns')):
            if event == 'start' or str(elem).find('text') == -1:
                if event != 'start' and str(elem).find('title') != -1:
                    article_title = unicode(elem.text).encode('utf8')
                    print article_title
            else:
                current_category = "Unknown"
                try:
                    current_category = unicode(elem.text).encode('utf8').split("Category:")[1]
                    current_category = current_category.split('|')[0]
                except Exception as ex:
                    pass
                # print current_category
                # print unicode(elem.text).encode('utf8')
                # print "*" * 100
                articles_parsed += 1
                break
                # if articles_parsed % 1000 == 0:
                #     print articles_parsed


if __name__ == '__main__':
    r = Reader('../data/wiki_dump.xml')
    r.parse_xml()
