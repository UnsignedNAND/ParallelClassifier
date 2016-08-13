import logging
from utils.config import get_conf

_CONF = get_conf()
_LOG = None


def get_log():
    global _LOG
    if not _LOG:
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] "
                                          "[%(levelname)-5.5s]  %(message)s")

        _LOG = logging.getLogger('wiki')

        try:
            log_file = _CONF['log']['path']
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_formatter)
            _LOG.addHandler(file_handler)
        except:
            pass

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        _LOG.addHandler(console_handler)

        conf_level = _CONF['log']['level']
        log_level = logging.DEBUG

        if conf_level == 'critical':
            log_level = logging.CRITICAL
        elif conf_level == 'error':
            log_level = logging.ERROR
        elif conf_level == 'warning':
            log_level = logging.WARNING
        elif conf_level == 'info':
            log_level = logging.INFO
        elif conf_level == 'debug':
            log_level = logging.DEBUG
        elif conf_level == 'notset':
            log_level = logging.NOTSET

        _LOG.setLevel(log_level)
    return _LOG
