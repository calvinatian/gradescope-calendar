from gradescopecalendar.gradescopecalendar import GradescopeCalendar


if __name__ == "__main__":
    # Modify these two fields with your Gradescope account details #
    EMAIL = "" 
    PASSWORD = ""
    # ------------------------------------------------------------ #

    result = GradescopeCalendar(EMAIL, PASSWORD, debug_on=True)
    result.write_to_ical()
