import logging

import caldav

logger = logging.getLogger(__name__)


class CalDav:
    def write_to_caldav(self, assignments_all: dict, url, calName, username, password, vtodo):
        """Write assignment details to a CalDAV server.

        Parameters
        ----------
        url : str
            the URL of the CalDAV server
        calName: str
            the name of the calendar to use (optional)
        username: str
            the username of the CalDAV user
        password: str
            the password of the CalDAV user
        vtodo: bool
            whether to add tasks to the calendar instead of events (default False)
        """
        with caldav.DAVClient(url=url, username=username, password=password) as client:
            calendar: caldav.Calendar
            if calName is not None:
                principal = client.principal()
                logger.info(
                    f"Found calendars: {[(calendar.name, calendar.id, calendar.url) for calendar in principal.calendars()]}")
                calendar = principal.calendar(name=calName)

            currentEvents: set[str] = self._get_caldav_current_assignments(calendar)

            for name, assignment in assignments_all.items():
                if f"{name} | {assignment.url}" in currentEvents:
                    logger.debug(f"Skipped Assignment <{name}> as it is already present.")
                    continue
                if vtodo:
                    calendar.save_todo(
                        summary=f"{name} | {assignment.url}",
                        due=assignment.close_date)
                else:
                    calendar.save_event(
                        summary=name,
                        location=assignment.url,
                        dtstart=assignment.close_date,
                        dtend=assignment.close_date)
                logger.debug(f"Wrote New Assignment <{name}> to CalDAV")

    def _get_caldav_current_assignments(self, calendar: caldav.Calendar) -> set[str]:
        events_raw: list[caldav.Event] = calendar.events()
        todos_raw: list[caldav.Todo] = calendar.todos(include_completed=True)
        assignments = set()

        for event_raw in events_raw:
            assignments.add(str(event_raw.vobject_instance.vevent.summary.value)+" | "+str(event_raw.vobject_instance.vevent.location.value))

        for todo_raw in todos_raw:
            assignments.add(str(todo_raw.vobject_instance.vtodo.summary.value))

        return assignments
