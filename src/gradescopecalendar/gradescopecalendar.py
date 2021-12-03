from gradescopecalendar.gradescope.pyscope import GSConnection
from gradescopecalendar.ical import ICal
from gradescopecalendar.gcal import GCal

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
    """

    def __init__(self, username: str, password: str, debug_on: bool = False):
        self.username = username
        self.password = password
        self.DEBUG = debug_on
        self.assignments_all = {}
        self._get_calendar_info()


    def _get_calendar_info(self) -> None:
        """Connect to Gradescope and get assignment information."""

        # TODO: Cache assignment details in file to reduce requests to Gradescope?
        #       Might not be necessary since course page lists all assignment details
        #       so only 1 request is made per course

        # Login to Gradescope
        session = GSConnection()
        session.login(self.username, self.password)

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

            if self.DEBUG:
                print(f"Done with course: {course.name}")

    def write_to_ical(self, path: str = None) -> str:
        ical = ICal()
        ical.write_to_ical(self.assignments_all, path)

    def write_to_gcal(self) -> None:
        gcal = GCal()
        gcal.write_to_gcal(self.assignments_all)
