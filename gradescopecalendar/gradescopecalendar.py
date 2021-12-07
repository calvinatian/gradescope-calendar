from gradescopecalendar.gradescope.pyscope import GSConnection
from gradescopecalendar.calendars.ical import ICal
from gradescopecalendar.calendars.gcal import GCal
import logging


logger = logging.getLogger(__name__)


class GradescopeCalendar:
    """Interface for interacting with Gradescope and calendar applications.

    Attributes
    ----------
    username : str
        email address to login as
    password : str
        password of the account
    DEBUG : bool
        controls whether additional debug info is printed
    assignments_all : dict[]
        collection of all assignments from all courses on Gradescope

    Methods
    -------
    write_to_ical()
        creates an iCalendar file (.ics) of all assignment details
    write_to_gcal()
        connects to Google Calendar API and updates or creates Gradescope assignments
    """

    def __init__(self, email: str, password: str) -> None:
        self.assignments_all = {}
        self._get_calendar_info(email, password)

    def _get_calendar_info(self, email: str, password: str) -> None:
        """Connect to Gradescope and get assignment information."""

        # TODO: Cache assignment details in file to reduce requests to Gradescope?
        #       Might not be necessary since course page lists all assignment details
        #       so only 1 request is made per course

        # Login to Gradescope
        session = GSConnection(email, password)

        session.account.add_courses_in_account()

        # Dictionary of all assignments current in the calendar
        self.assignments_all = {}
        # Loop through all course and assignments and make Google Calendar events
        for cnum in session.account.courses:
            course = session.account.courses[cnum]
            course._load_assignments()

            # Loop through all the assignments and save them
            for assignment in course.assignments.values():
                name = f"{assignment.name} - {assignment.course.name}"
                self.assignments_all[name] = assignment

            logger.debug(f"Done parsing course on Gradescope for: {course.name}")

    def write_to_ical(self, path: str = None) -> str:
        ical = ICal()
        ical.write_to_ical(self.assignments_all, path)

    def write_to_gcal(self) -> None:
        gcal = GCal()
        gcal.write_to_gcal(self.assignments_all)
