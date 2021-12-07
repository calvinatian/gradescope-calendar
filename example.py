from gradescopecalendar.gradescopecalendar import GradescopeCalendar
import logging

if __name__ == "__main__":
    # ------------------------------------------------------------ #
    # Modify these two fields with your Gradescope account details #
    EMAIL = ""
    PASSWORD = ""
    # Modify these for logging
    LOGGING_ENABLED = False
    LOGGING_LEVEL = logging.DEBUG
    # Valid logging levels
    # logging.INFO, logging.DEBUG, logging.WARN, logging.CRITICAL
    # ------------------------------------------------------------ #

    logger = logging.getLogger("gradescopecalendar" if LOGGING_ENABLED else __name__)
    logger.setLevel(logging.DEBUG)
    result = GradescopeCalendar(EMAIL, PASSWORD)
    result.write_to_ical()
    # Uncomment below to update Google Calendar directly
    # result.write_to_gcal()
