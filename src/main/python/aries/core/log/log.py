import logging.config


def setup_log(loglevel):
    """Setup log for application"""

    # create logger with 'spam_application'
    logger = logging.getLogger('aries')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('aries.log')
    fh.setLevel(loglevel)

    # create file handler which logs error messages
    eh = logging.FileHandler('error.log')
    eh.setLevel(logging.ERROR)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    eh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.addHandler(eh)
