import datetime


class GSAssignment:
    """
    A class used to govern Gradescope assignments.

    Attributes
    ----------
    name : str
        the name of the assignment
    aid : str
        7-digit assignment id of the assignment
    course : GSCourse
        course object assignment is attached to
    status : str
        status of the assignment: submitted, submitted-late, no-submission, open, open-late
    open_date : str
        open date of the assignment
    close_date : str
        close date of the assignment
    points : tuple (float, float)
        tuple of points earned and total points
    regrades_on : bool
        bool of whether assignment is currently accepting regrade requests
    questions : list [str]
        list of questions in the assignment
    """

    def __init__(
        self,
        name: str,
        aid: str,
        course,
        status: str,
        open_date: str,
        close_date: str,
        url: str = None,
        points: tuple[float, float] = (0, 0),
        regrades_on: bool = False,
        questions: list[str] = None,
    ):
        """Create a GSAssignment object"""
        self.name = name
        self.aid = aid
        self.course = course
        self.status = status
        self.open_date = datetime.datetime.strptime(open_date, "%Y-%m-%d %H:%M:%S %z")
        self.close_date = datetime.datetime.strptime(close_date, "%Y-%m-%d %H:%M:%S %z")
        self.current_date = datetime.datetime.now().astimezone()
        self.url = url
        self.time_left = (
            datetime.timedelta(0)
            if self.close_date < self.current_date
            else self.current_date - self.close_date
        )
        self.points = points
        self.regrades_on = regrades_on
        self.questions = questions

    def __str__(self):
        return f"[#Assignment# {self.name} ({self.aid}) Course: {self.course.name} \t| Points: {self.points} \t {self.status}]"
