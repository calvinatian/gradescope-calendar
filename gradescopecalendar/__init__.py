import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler = logging.FileHandler("gradescopecalendar.log")
formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.NullHandler())
