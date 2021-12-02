import requests
from bs4 import BeautifulSoup
from enum import Enum
from .account import GSAccount


class ConnState(Enum):
    INIT = 0
    LOGGED_IN = 1


class GSConnection:
    """The main connection class that keeps state about the current connection.

    Attributes
    ----------
    session : requests.Session
        the requests library Session object to manage authentication
    state : ConnState
        the state of the connection: INIT or LOGGED_IN
    account : GSAccount
        the account object created after logging into Gradescope

    Methods
    -------
    login(email, pwd)
        logs into Gradescope using passed in credentials
    """

    def __init__(self):
        """Initialize the session for the connection."""

        self.session = requests.Session()
        self.state = ConnState.INIT
        self.account = None

    def login(self, email: str, pwd: str) -> bool:
        """Login to Gradescope using passed in credentials.

        Note: some methods depend on account privillages

        Parameters
        ----------
        email : str
            the email address to login as
        pwd : str
            the password for the account
        """

        # Get auth_token
        init_resp = self.session.get("https://www.gradescope.com/")
        init_resp_parsed = BeautifulSoup(init_resp.text, "html.parser")
        # TODO: simplify this loop
        for form in init_resp_parsed.find_all("form"):
            if form.get("action") == "/login":
                for inp in form.find_all("input"):
                    if inp.get("name") == "authenticity_token":
                        auth_token = inp.get("value")

        # Login to Gradescope
        login_data = {
            "commit": "Log In",
            "utf8": "✓",
            "session[email]": email,
            "session[password]": pwd,
            "session[remember_me]": 0,
            "session[remember_me_sso]": 0,
            "authenticity_token": auth_token,
        }
        login_resp = self.session.post(
            "https://www.gradescope.com/login", params=login_data
        )

        # Verify login status
        if (
            len(login_resp.history) != 0
            and login_resp.history[0].status_code == requests.codes.found
        ):
            self.state = ConnState.LOGGED_IN
            self.account = GSAccount(self.session)
            return True
        raise Exception("Invalid credentials.")
