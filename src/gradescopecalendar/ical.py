import os.path
from icalendar import Calendar, Event
from icalendar import vText


class ICal:
    def write_to_ical(self, assignments_all: dict, path: str = None) -> None:
        """Write assignment details to .ics file.

        Parameters
        ----------
        path : str
            the path of the output file, defaults to the script location
        """

        if not path:
            path = os.path.dirname(os.path.abspath(__file__))

        # Extract relevant details from assignment for calendar event
        cal = Calendar()
        for name, assignment in assignments_all.items():
            end_time = assignment.close_date
            start_time = end_time  # Zero duration event for deadlines

            event = Event()
            event.add("summary", name)
            event.add("dtstart", start_time)
            event.add("dtend", end_time)
            event["location"] = vText(assignment.url)

            cal.add_component(event)

        # Write to file
        with open(f"{path}/gradescopecal.ics", "wb") as f:
            f.write(cal.to_ical())
            print(f"Wrote file to: {path}/gradescopecal.ics")
