import requests
from bs4 import BeautifulSoup
from gradescopecalendar.gradescope.account import GSAccount

from __future__ import annotations


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
    """

    def __init__(self, email: str, password: str):
        """Initialize the session for the connection to Gradescope.

        Parameters
        ----------
        email : str
            the email address of the Gradescope account to login as
        pwd : str
            the password for the account
        """

        self.session = requests.Session()
        self.account = None
        self._login(email, password)

    def _login(self, email: str, pwd: str) -> bool:
        """Login to Gradescope using passed in credentials.

        Note: some methods depend on account privillages

        Parameters
        ----------
        email : str
            the email address of the Gradescope account to login as
        pwd : str
            the password for the account

        Exceptions
        ----------
        ValueError
            Invalid credentials for the Gradescope account.
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
            self.account = GSAccount(self.session)
            return True
        raise ValueError("Invalid credentials.")
