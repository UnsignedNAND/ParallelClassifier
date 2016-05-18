import ConfigParser

CONF = None


def get_conf():
    global CONF

    if not CONF:
        parser = ConfigParser.ConfigParser()
        parser.readfp(open('wiki.conf'))
        CONF = {}
        for section in parser.sections():
            CONF[section] = {}
            for key, value in parser.items(section):
                if value.startswith('[') and value.endswith(']'):
                    value = value.replace('[', '').replace(']', '').split(',')
                CONF[section][key] = value
    return CONF

if __name__ == '__main__':
    get_conf()
