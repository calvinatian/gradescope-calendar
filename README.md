# Gradescope-Calendar

This script scrapes your Gradescope account for courses and assignment details. Assignment details currently can be transferred to iCalendar events (and then imported to other calendar applications such as Google Calendar). Another method exists to write these assignment details directly to a Google Calendar but requires additional setup. Scraping the Gradescope website is largely based off of the projects this is forked from.

## Requirements

* Python 3
* Git

## Installation

### Development

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
python3 -m venv .venv
.venv/Scripts/activate
pip3 install -r requirements.txt
```

## Usage

An example script is located at `example.py`. Modify the `EMAIL` and `PASSWORD` fields with your Gradescope account information then run the script.

```bash
./example.py
```

## Advanced settings

### Google Calendar

1. Create new Google API Application
2. Enable Google Calendar API
3. ...
