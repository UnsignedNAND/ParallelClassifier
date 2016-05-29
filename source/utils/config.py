import configparser

_CONF = None


def get_conf():
    global _CONF

    if not _CONF:
        parser = configparser.ConfigParser()
        parser.read_file(open('wiki.conf'))
        _CONF = {}
        for section in parser.sections():
            _CONF[section] = {}
            for key, value in parser.items(section):
                if value.startswith('[') and value.endswith(']'):
                    value = value.replace('[', '').replace(']', '').split(',')
                _CONF[section][key] = value
    return _CONF

if __name__ == '__main__':
    get_conf()
