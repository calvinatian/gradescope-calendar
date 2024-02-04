from gradescopecalendar.gradescopecalendar import GradescopeCalendar
import logging

if __name__ == "__main__":
    # ------------------------------------------------------------ #
    # Modify these two fields with your Gradescope account details #
    EMAIL = ""
    PASSWORD = ""
    IS_INSTRUCTOR = False  # If you are an instructor for **any** course,
                           # modify this to True.
    # Modify these for logging
    LOGGING_ENABLED = True
    LOGGING_LEVEL = logging.DEBUG
    # Valid logging levels
    # logging.INFO, logging.DEBUG, logging.WARN, logging.CRITICAL
    # ------------------------------------------------------------ #

    logger = logging.getLogger("gradescopecalendar" if LOGGING_ENABLED else None)
    logger.setLevel(LOGGING_LEVEL)
    calendar = GradescopeCalendar(EMAIL, PASSWORD, IS_INSTRUCTOR)
    calendar.write_to_ical()
    # Uncomment below to update Google Calendar directly
    # calendar.write_to_gcal()
    # Uncomment below to write to a CalDAV server (this example assumes a nextcloud server)
    # calendar.write_to_caldav(
    #     url="https://<nextcloud-hostname>/remote.php/dav/calendars/<nextcloud-user>/",
    #     calName="Gradescope", # Create a calendar with this name
    #     username="<nextcloud-user>",
    #     password="<nextcloud-app-password>"
    # )
