import logging
import os


class MyLogger:
    LogFilePath = os.path.abspath(os.path.join((os.getcwd()).split('iDDU')[0], 'iDDU', 'data', 'iDDU.log'))

    logger = logging.getLogger('iDDULogger')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s || %(message)s')

    file_handler = logging.FileHandler(LogFilePath)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    error = logger.error
    werning = logger.warning
    info = logger.info
    debug = logger.debug
    critical = logger.critical

    def __init__(self):
        pass
