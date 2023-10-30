# prayer-times-to-google-calendar

A code that uses an API to fetch prayer times, and slots them into a google calendar

## Set-up and installation instructions

1. Create venv `python3 -m venv venv`
2. Activate venv `source .\venv\bin\activate`
3. Get credentials from google API and save as credentials.json
4. Install Requirements `pip3 install -r requirements.txt`
5. Run `pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
6. Run `python3 quickstart.py`

## Development Instructions

- Run `python3 uploader.py`
- The chosen calendar will be filled with prayer times :)

## To make it a .exe

- Run the setup and installation instructions
- Run `pyinstaller -F uploader.py`
- Find the .exe file in the dist folder
