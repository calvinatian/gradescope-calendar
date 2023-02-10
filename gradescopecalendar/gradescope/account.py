from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from gradescopecalendar.gradescope.course import GSCourse


class GSAccount:
    """A class used to govern Gradescope accounts.

    Attributes
    ----------
    session : requests.Session
        the requests library Session object to manage authentication
    courses : dict(str : GSCourse)
        dictionary using course ID as key and GSCourse as value

    Methods
    -------
    add_courses_in_account()
        adds all courses available in user account
    add_course()
    """

    def __init__(self, session: requests.Session):
        self.session = session
        self.courses = {}

    def add_courses_in_account(self, is_instructor: bool = False) -> None:
        """Finds all courses in the current user account and adds them"""

        # Get account page and parse it using bs4
        account_resp = self.session.get("https://www.gradescope.com/account")
        account_resp_parsed = BeautifulSoup(account_resp.text, "html.parser")

        # Parameters
        ACCOUNT_COURSES_CLASS = "pageHeading"
        # TODO:  Add way to add instructor courses to calendar?
        ACCOUNT_COURSES_HEADING = "Student Courses" if is_instructor else "Your Courses"
        COURSE_CLASS = "courseBox"
        COURSE_SHORTNAME_CLASS = "courseBox--shortname"
        COURSE_NAME_CLASS = "courseBox--name"

        courses = account_resp_parsed.find(
            "h1",
            class_=ACCOUNT_COURSES_CLASS,
            string=ACCOUNT_COURSES_HEADING,
            # text="Student Courses",
        ).next_sibling

        for course in courses.find_all("a", class_=COURSE_CLASS):
            short_name = course.find("h3", class_=COURSE_SHORTNAME_CLASS).text
            name = course.find("div", class_=COURSE_NAME_CLASS).text
            cid = course.get("href").split("/")[-1]

            year = None
            for tag in course.parent.previous_siblings:
                if tag.get("class") == "courseList--term pageSubheading":
                    year = tag.body
                    break
            self.add_course(cid=cid, name=name, short_name=short_name, year=year)

    def add_course(self, cid: str, name: str, short_name: str, year: str) -> None:
        """Creates a GSCourse object and adds it to the courses dictionary.

        Parameters
        ----------
        cid : str
            8-digit course ID
        name : str
            full name of the course
        shortname : str
            shortname of the course
        year : str
            year of the course
        """

        self.courses[cid] = GSCourse(
            cid=cid, name=name, short_name=short_name, year=year, session=self.session
        )
