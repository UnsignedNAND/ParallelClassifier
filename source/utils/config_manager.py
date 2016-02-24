import ConfigParser


def get_conf():
    parser = ConfigParser.ConfigParser()
    parser.readfp(open('../wiki.conf'))

    config = {}
    for section in parser.sections():
        config[section] = {}
        for key, value in parser.items(section):
            if value.startswith('[') and value.endswith(']'):
                value = value.replace('[', '').replace(']', '').split(',')
            config[section][key] = value

if __name__ == '__main__':
    get_conf()
