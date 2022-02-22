import time
import datetime
import os.path
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from __future__ import annotations

# If modifying these scopes, delete the file token.json.
# calendar                      See, edit, share, and permanently delete all the calendars you can access using Google Calendar
# calendar.events               View and edit events on all your calendars
# calendar.events.readonly      View events on all your calendars
# calendar.readonly             See and download any calendar you can access using your Google Calendar
# calendar.settings.readonly    View your Calendar settings
SCOPES = ["https://www.googleapis.com/auth/calendar"]

logger = logging.getLogger(__name__)


class GCal:
    """A class to handle connection with Google Calendar."""

    # API setup taken from Google docs quickstart
    def _gcal_api_setup(self):
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

    def _find_gradescope_calendar(self, service) -> dict:
        """Finds or creates the Gradescope calendar and return its information."""

        # Search for existing calendar and create if needed
        user_calendars = service.calendarList().list().execute()
        gs_cal = None

        # Find existing Gradescope calendar by searching names
        for calendar in user_calendars["items"]:
            if calendar.get("summary", "") == "Gradescope":
                gs_cal = calendar
                break

        # Make a new Gradescope calendar
        if not gs_cal:
            logger.info(f"No existing Gradescope calendar, creating a new calendar...")
            gs_cal_new = {
                "kind": "calendar#calendarListEntry",
                "description": "Unofficial integration with Gradescope to integrate assignment deadlines to Google Calendar",
                "summary": "Gradescope",
            }
            gs_cal = service.calendars().insert(body=gs_cal_new).execute()
            logger.debug(f"Made a new calendar!\n{gs_cal}")
        logger.debug(f"Calendar already exists!\n{gs_cal}")
        return gs_cal

    def _get_gcal_current_assignments(self, service, gs_cal_id: str) -> dict:
        """Connects to the Gradescope calendar on Google Calendar and gets all event details.

        Parameters
        ----------
        service : googleapiclient.discovery.Resource
            resource object to interact with Google API
        gs_cal_id : str
            ID of the Gradescope calendar on Google Calendar
        """

        current_assignments = {}
        page_token = None

        # Loop through all events
        while True:
            assignment_list = (
                service.events()
                .list(calendarId=gs_cal_id, pageToken=page_token)
                .execute()
            )
            for event in assignment_list["items"]:
                name = event["summary"]
                current_assignments[name] = event
            page_token = assignment_list.get("nextPageToken")
            if not page_token:
                break

        return current_assignments

    def write_to_gcal(self, assignments_all: dict) -> bool:
        """Connects to Google Calendar API to add events for Gradescope assignments.

        Parameters
        ----------
        assignments_all : dict
            all assignments from Gradescope
        """

        # Connect to Google Calendar API service
        service = self._gcal_api_setup()

        # Search for existing calendar and create if needed
        gs_cal = self._find_gradescope_calendar(service)

        # Loop through all current assignments on Google Calendar and get their info
        current_assignments = self._get_gcal_current_assignments(
            service=service, gs_cal_id=gs_cal["id"]
        )

        # Loop through all assignments from Gradescope and update/create events in Google Calendar as needed
        # Priority given to Gradescope for {open time, close time, location}
        # Priority given to Google Calendar for all other fields
        EPOCHTIME = "1970-01-01T00:00:00+0000"
        for name, assignment in assignments_all.items():
            # Format time to match time from API
            end_time = datetime.datetime.strftime(
                assignment.close_date, "%Y-%m-%dT%H:%M:%S%z"
            )
            start_time = end_time  # Zero duration event

            event_mode = None
            event_body = None
            # Update existing event details
            if name in current_assignments:
                # Attributes to compare between Google Calendar and Gradescope
                is_different_url = (
                    assignment.url != ""
                    and current_assignments[name].get("location", "") != assignment.url
                )
                is_different_start = assignment.open_date not in (
                    EPOCHTIME,
                    "",
                ) and current_assignments[name]["start"]["dateTime"] != time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", assignment.close_date.utctimetuple()
                )
                is_different_end = assignment.close_date not in (
                    EPOCHTIME,
                    "",
                ) and current_assignments[name]["end"]["dateTime"] != time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ",
                    assignment.close_date.utctimetuple(),
                )

                # Only modify events with divergent urls, start, or end times to speed up execution
                if is_different_url or is_different_start or is_different_end:
                    # Check if assignment url exists and update if different from gcal
                    if is_different_url:
                        logger.debug("URL location will be updated")
                        current_assignments[name]["location"] = assignment.url
                    # Check if assignment open date exists and update if different from gcal
                    elif is_different_start:
                        logger.debug("Start time will be updated")
                        current_assignments[name]["start"]["dateTime"] = start_time
                    # Check if assignment close date exists and update if different from gcal
                    elif is_different_end:
                        logger.debug("End time will be updated")
                        current_assignments[name]["end"]["dateTime"] = end_time
                    event_mode = "update"
                    event_body = current_assignments[name]

            # Create new event details
            elif assignment.close_date != EPOCHTIME:
                logger.debug(f"Creating new event {name}")
                event_mode = "create"
                event_body = {
                    "summary": name,
                    "location": assignment.url,
                    "start": {
                        "dateTime": start_time,
                    },
                    "end": {
                        "dateTime": end_time,
                    },
                }

            if event_mode != None:
                try:
                    self._gcal_event_modify(
                        mode=event_mode,
                        service=service,
                        gs_cal_id=gs_cal["id"],
                        event_body=event_body,
                        event_id=current_assignments[name].get("id", None)
                        if name in current_assignments
                        else None,
                    )
                    time.sleep(0.25)  # Delay to help with rate limits
                except ValueError as e:
                    logger.exception(e)

            logger.debug(f"Google Calendar: done with assignment: {assignment.name}")

    # create new gcal event
    def _gcal_event_modify(
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

        if mode.lower() == "create":
            logger.debug(f"Creating a new gcal event...")
            event = (
                service.events().insert(calendarId=gs_cal_id, body=event_body).execute()
            )
            logger.info(f"Event created: {event.get('htmlLink')}")
        elif mode.lower() == "update":
            logger.debug(f"Updating a gcal event...")
            updated_event = (
                service.events()
                .update(calendarId=gs_cal_id, body=event_body, eventId=event_id)
                .execute()
            )
            logger.info(f"Event update: {updated_event.get('htmlLink')}")
        else:
            raise ValueError(f"Invalid mode {mode} for {event_body.get('name')}")
        logger.debug(f"Done modifying event")
