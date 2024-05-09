"""This module contains code retrieving prayer times from the API and transferring them onto a google calendar"""
from quickstart import *
from tqdm import tqdm
import requests
import json
import os
import sys
from datetime import datetime, timedelta


def find_file_path() -> str:
    """Finds the path to the folder when run and returns it"""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path


def get_monthly_prayer_time_data_from_api(year_input: str, month_input: str) -> str:
    """Sends request to API to get a response with all prayer times as json"""
    response = requests.get(f'https://www.londonprayertimes.com/api/times/?format=json&key=3d07d979-1145-4d4e-81d0-8fac6e634a2d&year={year_input}&month={month_input}&24hours=true')
    data = json.loads(response.text)
    return data["times"]
        

def create_calendar_event(date: str, time: str, prayer: str, credential) -> None:
    """Creates the calendar events using google api"""
    time = str(datetime.strptime(time, "%H:%M"))[11:16]
    event = {
        'start': {
            'dateTime': f'{date}T{time}:00',
            'timeZone': 'Europe/London'
        },
        'end': {
            'dateTime': f'{date}T{time}:59',
            'timeZone': 'Europe/London'
        },
        'summary': prayer,
        'description': prayer
    }

    service = build('calendar', 'v3', credentials=credential)

    event = service.events().insert(calendarId='32a0cadd415aa98eb31eeb3a492dddc2b22006d46b245beb16b92152024b1d31@group.calendar.google.com', body=event).execute()


def delete_events(credents):
    # Specify the date range for events deletion
    start_date = datetime(2024, 5, 1, 0, 0, 0)
    end_date = datetime(2024, 7, 1, 0, 0, 0)

    service = build('calendar', 'v3', credentials=credents)

    # Get calendar ID by calendar name
    calendar_id = '32a0cadd415aa98eb31eeb3a492dddc2b22006d46b245beb16b92152024b1d31@group.calendar.google.com'

    # Fetch events within the specified date range
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_date.isoformat() + 'Z',
        timeMax=end_date.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    # Delete each event within the date range
    if 'items' in events_result:
        for event in events_result['items']:
            event_id = event['id']
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Event '{event['summary']}' deleted.")


if __name__ == '__main__':

    path = find_file_path()

    creds = Credentials.from_authorized_user_file(f'{path}/token.json', SCOPES)

    year = input('Please input the year that you want the times for (in digits [e.g.2023]): ')

    if year == 'clear':
        delete_events(creds)
        exit()

    month = input('Please input the month that you want the times for (in lowercase [e.g. november]): ')

    months_list = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

    prayer_times_json = get_monthly_prayer_time_data_from_api(year, month)

    creds = Credentials.from_authorized_user_file(f'{path}/token.json', SCOPES)

    prayers = ['fajr', 'sunrise', 'dhuhr', 'asr_2', 'magrib', 'isha']
    for day in tqdm(prayer_times_json):
        for prayer in prayer_times_json[day]:
            if prayer in prayers:
                prayer_time = prayer_times_json[day][prayer]
                create_calendar_event(day, prayer_time, prayer, creds)
    print("Check your calendar at the month and year you inputted. You will find London prayer times there.")
