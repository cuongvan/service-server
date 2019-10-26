import logging
from flask.logging import wsgi_errors_stream
import project_conf

if project_conf.debug:
    log_formatter = logging.Formatter("[%(name)s]\t%(levelname)s: %(message)s")
else:
    log_formatter = logging.Formatter(
            fmt="[%(name)s]\t[%(asctime)s] %(levelname)s: %(message)s",
            datefmt='%d/%b/%Y %H:%M:%S')# 26/Oct/2019 10:40:05

def create_logger(name, level=logging.DEBUG):
    if '.' in name: # nested module name
        name = name.rpartition('.')[2] # just get the file name from module name

    logger = logging.getLogger(name)

    # copy from flask.logging -> default_handler
    handler = logging.StreamHandler(wsgi_errors_stream)
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
