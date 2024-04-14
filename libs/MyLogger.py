import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import traceback


class MyLogger:

    LogFilePath = os.path.abspath(os.path.join((os.getcwd()).split('iDDU')[0], 'iDDU', 'data', 'iDDU.log'))

    logger = logging.getLogger('iDDULogger')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s || %(message)s')

    # file_handler = logging.FileHandler(LogFilePath)
    file_handler = RotatingFileHandler(LogFilePath, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    error = logger.error
    warning = logger.warning
    info = logger.info
    debug = logger.debug
    critical = logger.critical

    def __init__(self):
        pass


class ExceptionHandler(object):

    def __init__(self, func):
        self.SError = None
        pass

    def exception_handler(self, func):
        def inner_function(*args, **kwargs):
            print('asdfghjjhgfds')
            return func(*args, **kwargs)
            # try:
            #     func(*args, **kwargs)
            #
            # except Exception as e:
            #
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #     tracebackString = traceback.format_exc()
            #     ErrorString = '{} in Function <{}> in <{}>\n{}'.format(exc_type, func.__name__, fname, tracebackString)
            #
            #     if not self.SError == ErrorString:
            #         MyLogger.error(ErrorString)
            #         self.SError = ErrorString
            #         print(self.SError)

        return inner_function
