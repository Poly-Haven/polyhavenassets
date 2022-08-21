import logging

log = logging.getLogger(__name__)


def inspect(obj):
    log.debug("---------------------------- INSPECT ----------------------------")
    for attr in dir(obj):
        value = getattr(obj, attr)
        log.debug(f"{attr} \t ({type(value)})\t=\t{value}")
