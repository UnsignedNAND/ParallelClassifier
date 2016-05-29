import logging
from utils.config_manager import get_conf

conf = get_conf()
_LOG = None


def get_logger():
    global _LOG
    if not logger:
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] "
                                          "[%(levelname)-5.5s]  %(message)s")
        log_file = conf['log']['path']

        logger = logging.getLogger('wiki')

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

        conf_level = conf['log']['level']
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

        logger.setLevel(log_level)
    return logger
