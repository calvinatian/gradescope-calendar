import time
import datetime
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from gradescopecalendar.gradescope.pyscope import GSConnection


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

DEBUG = False

class GCal:
    """A class to handle connection with Google Calendar."""

    # create new gcal event
    def gcal_event_modify(
        self, service, gs_cal_id: str, event_body: dict, mode: str, event_id: str = None
    ) -> None:
        """Creates or updates a Google Calendar event.

        Parameters
        ----------
        mode : str
            "create", "update"
        service : googleapiclient.discovery.Resource
            resource object to interact with Google API
        gs_cal_id : str
            ID of the Gradescope calendar
        event_body : dict
            details about the calendar event to modify
        event_id : str (optional)
            eventID to update
        """

        DEBUG = self.debug

        if mode.lower() == "create":
            if self.DEBUG:
                print(f"Creating a new gcal event...")
            event = (
                service.events().insert(calendarId=gs_cal_id, body=event_body).execute()
            )
            if DEBUG:
                print(f"Event created: {event.get('htmlLink')}")
        elif mode.lower() == "update":
            if DEBUG:
                print(f"Updating a gcal event...")
            updated_event = (
                service.events()
                .update(calendarId=gs_cal_id, body=event_body, eventId=event_id)
                .execute()
            )
            if DEBUG:
                print(f"Event update: {updated_event.get('htmlLink')}")
        if DEBUG:
            print(f"Done modifying event")

    def find_gradescope_calendar(self, service):
        """Finds or creates the Gradescope calendar and return its information."""

        # Search for existing calendar and create if needed
        user_calendars = service.calendarList().list().execute()
        gs_cal = None
        for calendar in user_calendars["items"]:
            if calendar.get("summary", "") == "Gradescope":
                gs_cal = calendar
                break
        if not gs_cal:  # make a new calendar
            if DEBUG:
                print(f"No existing Gradescope calendar, creating a new calendar...")
            gs_cal_new = {
                "kind": "calendar#calendarListEntry",
                "description": "Unofficial integration with Gradescope to integrate assignment deadlines to Google Calendar",
                "summary": "Gradescope",
            }
            gs_cal = service.calendars().insert(body=gs_cal_new).execute()
            if DEBUG:
                print(f"Made a new calendar!\n{gs_cal}")
        elif DEBUG:
            print(f"Calendar already exists!")
        return gs_cal

    # API setup taken from Google docs quickstart
    def gcal_api_setup(self):
        """Setup connection to Google Calendar API"""

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)
        return service

    def insert_to_gcal(self) -> bool:
        """Connects to Google Calendar API to add events for Gradescope assignments."""

        # Connect to Google Calendar API
        service = self.gcal_api_setup()

        # Search for existing calendar and create if needed
        gs_cal = self.find_gradescope_calendar(service)

        # Login to Gradescope
        session = GSConnection()
        session.login(self.username, self.password)

        session.account.add_courses_in_account()

        # Loop through all course and assignments and make Google Calendar events
        for cnum in session.account.courses:
            course = session.account.courses[cnum]
            course._load_assignments()
            assignments_all = (
                {}
            )  # Dictionary of all assignments current in the calendar

            # Loop through all current assignments and get their info
            page_token = None
            while True:
                assignments_list = (
                    service.events()
                    .list(calendarId=gs_cal["id"], pageToken=page_token)
                    .execute()
                )
                for event in assignments_list["items"]:
                    name = event["summary"]
                    assignments_all[name] = event
                page_token = assignments_list.get("nextPageToken")
                if not page_token:
                    break

            for assign in course.assignments.values():  # Just loop through the values
                end_time = datetime.datetime.strftime(
                    assign.close_date, "%Y-%m-%dT%H:%M:%S%z"
                )
                # start_time = datetime.datetime.strftime(
                #     assign.close_date - datetime.timedelta(minutes=15),
                #     "%Y-%m-%dT%H:%M:%S%z",
                # )
                start_time = end_time

                name = f"{assign.name} - {assign.course.name}"
                EPOCHTIME = "1970-01-01T00:00:00+0000"

                if name in assignments_all:  # Update event
                    if (
                        assignments_all[name].get("location", "") != assign.url
                        or assignments_all[name]["start"]["dateTime"]
                        != time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ",
                            datetime.datetime.strptime(
                                start_time, "%Y-%m-%dT%H:%M:%S%z"
                            ).utctimetuple(),
                        )
                        or assignments_all[name]["end"]["dateTime"]
                        != time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ",
                            datetime.datetime.strptime(
                                end_time, "%Y-%m-%dT%H:%M:%S%z"
                            ).utctimetuple(),
                        )
                    ):  # Update necessary
                        if self.DEBUG:
                            print(f"updating {name}")
                        assignments_all[name]["location"] = assign.url
                        assignments_all[name]["start"]["dateTime"] = start_time
                        assignments_all[name]["end"]["dateTime"] = end_time
                        self.gcal_event_modify(
                            mode="update",
                            service=service,
                            gs_cal_id=gs_cal["id"],
                            event_id=assignments_all[name]["id"],
                            event_body=assignments_all[name],
                        )
                        time.sleep(0.5)  # Delay to help with rate limits

                elif end_time != EPOCHTIME:  # Create new event
                    if self.DEBUG:
                        print(f"creating {name}")
                    event_body = {
                        "summary": name,
                        "location": assign.url,
                        "start": {
                            "dateTime": start_time,
                        },
                        "end": {
                            "dateTime": end_time,
                        },
                    }
                    self.gcal_event_modify(
                        mode="create",
                        service=service,
                        gs_cal_id=gs_cal["id"],
                        event_body=event_body,
                    )
                    time.sleep(0.5)  # Delay to help with rate limits

            if self.DEBUG:
                print(f"Done with course: {course.name}")
