# Gradescope-Calendar

[![PyPi version](https://badgen.net/pypi/v/gradescopecalendar/)](https://pypi.org/project/gradescopecalendar/)

This script scrapes your Gradescope account for courses and assignment details. Assignment details currently can be transferred to iCalendar events (and then imported to other calendar applications such as Google Calendar). Another method exists to write these assignment details directly to a Google Calendar but requires additional setup. Scraping the Gradescope website is largely based off of the projects this is forked from.

- [Gradescope-Calendar](#gradescope-calendar)
  - [Requirements](#requirements)
  - [Installation](#installation)
    - [Upgrade](#upgrade)
    - [Development](#development)
  - [Usage](#usage)
    - [Automatically running](#automatically-running)
      - [Windows](#windows)
      - [Linux](#linux)
      - [Mac](#mac)
  - [Advanced settings](#advanced-settings)
    - [Google Calendar](#google-calendar)
      - [Notes](#notes)
    - [Future Plans](#future-plans)

## Requirements

* Python 3.7 or above

## Installation

Windows

```bash
python -m venv .venv
.venv/Scripts/activate
pip install gradescopecalendar
```

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install gradescopecalendar
```

### Upgrade

Windows

```bash
pip install --upgrade gradescopecalendar
```

Mac/Linux

```bash
pip3 install --upgrade gradescopecalendar
```


### Development

These steps are only necessary if you wish to install or work on the development version.

Windows

```bash
git clone https://github.com/calvinatian/gradescope-calendar.git
cd gradescope-calendar
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

Mac/Linux

```bash
git clone https://github.com/calvinatian/gradescope-calendar.git
cd gradescope-calendar
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

Copy paste the below code or use the example script located at `example.py`. Modify the `EMAIL` and `PASSWORD` fields with your Gradescope account information then run the script.

```py
from gradescopecalendar.gradescopecalendar import GradescopeCalendar
import logging

if __name__ == "__main__":
    # ------------------------------------------------------------ #
    # Modify these two fields with your Gradescope account details #
    EMAIL = ""
    PASSWORD = ""
    IS_INSTRUCTOR = False  # If you are an instructor for **any** course,
                           # modify this to True.
    # Modify these for logging
    LOGGING_ENABLED = True
    LOGGING_LEVEL = logging.DEBUG
    # Valid logging levels
    # logging.INFO, logging.DEBUG, logging.WARN, logging.CRITICAL
    # ------------------------------------------------------------ #

    logger = logging.getLogger("gradescopecalendar" if LOGGING_ENABLED else None)
    logger.setLevel(LOGGING_LEVEL)
    calendar = GradescopeCalendar(EMAIL, PASSWORD, IS_INSTRUCTOR)
    calendar.write_to_ical()
    # Uncomment below to update Google Calendar directly
    # calendar.write_to_gcal()
```

Details about the application are written to the log file `gradescopecalendar.log` if enabled.

### Automatically running

#### Windows

##### Windows task scheduler

Windows task scheduler can be used to automatically run the script at a specified interval. This can be done by creating a new task and setting the trigger to run the script at a specified interval. When creating the task you should see a window with 5 tabs: General, Triggers, Actions, Conditions, and Settings. The following steps will walk you through the process of creating a task to run the script every day at 8:00 AM and every time you unlock your device. An additional condition will be added so the previous triggers will only execute if the computer has been idle for 10 minutes.

###### General

General information about the task

1. Give the task a name and description.
2. Everything else can be left as default.

###### Triggers

The trigger is what will cause the task to run. In this case we want the task to run every day at 8:00 AM and when we unlock the device.

1. Click "New".
2. Select "Daily" and set the time to 8:00 AM.
3. The other settings can be left default but feel free to change them if you want.
4. Click "OK".
5. Click "New".
6. At the top in the "Begin the task" dropdown select "On workstation unlock".
7. Click "OK".

###### Actions

This is where we will specify the program to run and the arguments to pass to the program.

1. Click "New".
2. For the "Program/script" field, navigate to your `python.exe` executable location. If you are using a virtual environment, it would be `\PATH\TO\FOLDER\.venv\Scripts\python.exe`.
3. In the arguments field you should specify the path to the script. For example, if the script is located in `C:\Users\user\gradescope-calendar\example.py` then the arguments would be `C:\Users\user\gradescope-calendar\example.py`.
4. The "Start in" field should be the path to the folder containing the script. For example, if the script is located in `C:\Users\user\gradescope-calendar\example.py` then the "Start in" field would be `C:\Users\user\gradescope-calendar`.
5. Click "OK".

###### Conditions

This is where we will specify the conditions that must be met for the task to run. In this case we want the task to run only if the computer has been idle for 10 minutes.

1. Click "New".
2. Select "Start the task only if the computer is idle for" and change the time to 10 minutes.
3. Uncheck "Stop if the computer ceases to be idle"
4. Check the box under Network to "Start only if the following network connection is available".
5. Click "OK".

###### Settings

This is where we will specify additional settings for the task.

1. Click "New".
2. Select "Run task as soon as possible after a scheduled start is missed".
3. Click "OK".

The task should now be scheduled to run every day at 8:00 AM and every time you unlock your device only if the device has been idle for 10 minutes. By default, it will wait up to 1 hour for this condition to come true (feel free to change the time in the "Conditions" tab). If it misses the scheduled start time it will run as soon as possible after the scheduled start time is missed.

#### Linux

Cron

#### Mac

Launchd

## Advanced settings

### Google Calendar

1. Goto the [Google Cloud Platform](https://console.cloud.google.com) and create a new project.
2. From the sidebar click "APIs & Services" and then "Dashboard".
3. At the top of the page click "Enable API and Services".
4. Scroll down to the Google Calendar API and enable it.
5. Goto the sidebar and click on "OAuth consent screen".
6. Click on "External".
7. Fill in the App information. Since this API instance will only be used by yourself it does not really matter what you fill in.
8. You can skip filling in the "Scopes" section. Just click "Save and Continue".
9. On the "Test users" add the email(s) you want to modify the calendars for. If you are paranoid about the script altering your private calendar details you can create a new Google account and add that instead. Then you can share that calendar to other Google accounts.
10. On the sidebar goto the "Credentials" tab and create a new "OAuth Client ID".
11. Select Desktop app for Application type and give it any name.
12. Once the ID has been created, click the "Download JSON" button and save the file to your computer as `credentials.json` and move it to where you are using `gradescopecalendar`.
13. You can now uncomment the line for writing to Google Calendar and run the script.

#### Notes

* On first run you will be prompted to login and grant access to your account for the project. This will create a `token.json` in the folder granting access to the script to modify your calendar. No one should be able to access your account if this file is kept secure. As mentioned earlier, you can also create a new Google account and use that calendar instead. Then you can share that calendar with your other Google accounts.
* You might notice nothing being printed to the console when running the script. This is intentional. Enable logging and check the `gradescopecalendar.log` for details about the script progress.
* The first run of writing to Google Calendar may take a while depending on how many assignments there are to create/modify. Subsequent runs should be much faster as only new or updated assignments will be created/modified.
* Calendar events on the Gradescope calendar are never deleted, only created or updated. If the name of an assignment changes a new event will be created with the new name. Otherwise, if the start/end time or the location (URL of the assignment) of the event differ between Gradescope and Google Calendar, the event will be updated with the values from Gradescope. All other fields such as the description should remain unchanged.

### Future Plans

* More use options such as the naming format of the events and how much to offset the start time by (currently start time is the same as end time).
* Ability to add custom reminders for Google Calendar events.
