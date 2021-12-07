import requests
import re
from bs4 import BeautifulSoup
from gradescopecalendar.gradescope.assignment import GSAssignment


class GSCourse:
    """A class used to govern Gradescope courses.

    Attributes
    ----------
    name : str
        the full name of the course
    short_name : str
        the short name of the course
    cid : str
        6-digit course id of the course
    year : str
        the year of the course
    session : requests.Session
        the requests library Session object to manage authentication
    assignments : dict
        the available assignments in the course
    """

    def __init__(
        self, name: str, short_name: str, cid: str, year: str, session: requests.Session
    ) -> None:
        """Create a course object that has lazy eval'd assignments"""
        self.name = name
        self.course_code = short_name
        self.cid = cid
        self.year = year
        self.session = session
        self.assignments = {}
        # self._load_assignments()

    def __str__(self) -> None:
        return f"[#Course# {self.short_name} ({self.cid}) {self.name} ]"

    def _load_assignments(self) -> None:
        """Load the assignments available from the course."""

        EPOCHTIME = "1970-01-01 00:00:00 +0000"
        INVALID_ASSIGNMENT_ID = "0000000"

        assignment_resp = self.session.get(
            f"https://www.gradescope.com/courses/{self.cid}/"
        )
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, "html.parser")

        assignment_table = []
        for assignment_row in parsed_assignment_resp.findAll("tr", role="row")[
            1:
        ]:  # Skip header row
            row = []
            for th in assignment_row.findAll("th"):
                row.append(th)
            for td in assignment_row.findAll("td"):
                row.append(td)
            assignment_table.append(row)

        for row in assignment_table:
            name = row[0].text
            try:  # Assignment ID not guaranteed to be available
                aid = re.search(
                    r"/.*/assignments/(.+?)/", row[0].find("a").get("href")
                ).group(1)
            except (IndexError, AttributeError):
                aid = INVALID_ASSIGNMENT_ID
            try:  # Points not guaranteed
                points = row[1].text.split(" / ")
                points_earned = float(points[0])
                points_total = float(points[1])
                status = "Submitted"
            except (IndexError, ValueError):
                points_earned = -1
                points_total = -1
                status = row[1].text
            try:  # Open and close date not guaranteed to be available
                open_date = row[3].text if row[3].text != "" else EPOCHTIME
                close_date = row[4].text if row[4].text != "" else EPOCHTIME
            except IndexError:
                open_date = EPOCHTIME
                close_date = EPOCHTIME
            # TODO: Determine location of regrade flag
            regrades_on = False

            self.assignments[name] = GSAssignment(
                name=name,
                aid=aid,
                course=self,
                status=status,
                open_date=open_date,
                close_date=close_date,
                points=(points_earned, points_total),
                regrades_on=regrades_on,
                url=f"https://www.gradescope.com/courses/{self.cid}/assignments/{aid}/" if aid != INVALID_ASSIGNMENT_ID else "",
            )
