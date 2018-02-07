import logging

def getLogger():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    return logger
