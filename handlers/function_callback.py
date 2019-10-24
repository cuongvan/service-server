import logging

logger = logging.getLogger(__name__)

def process_callback(data):
    logger.info(data)
    return ''
