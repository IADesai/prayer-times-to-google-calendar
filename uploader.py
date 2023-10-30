"""This module contains code retrieving prayer times from the API and transferring them onto a google calendar"""
from quickstart import *
import requests
import json
from datetime import datetime, timedelta


def get_monthly_prayer_time_data_from_api(year_input: str, month_input: str) -> str:
    """Sends request to API to get a response with all prayer times as json"""
    response = requests.get(f'https://www.londonprayertimes.com/api/times/?format=json&key=3d07d979-1145-4d4e-81d0-8fac6e634a2d&year={year_input}&month={month_input}&24hours=true')
    data = json.loads(response.text)
    return data["times"]
        

def create_calendar_event(date: str, time: str, prayer: str, credential) -> None:
    """Creates the calendar events using google api"""
    time = str(datetime.strptime(time, "%H:%M")-timedelta(minutes=1))[11:16]
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

    event = service.events().insert(calendarId='1a4a4046ea518584fe2a3a0dc2dcffc889427489a999182a13214a1c2c5d830c@group.calendar.google.com', body=event).execute()


if __name__ == '__main__':

    year = input('Please input the year that you want the times for (in digits [e.g.2023]): ')
    month = input('Please input the month that you want the times for (in lowercase [e.g. november]): ')

    prayer_times_json = get_monthly_prayer_time_data_from_api(year, month)

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    prayers = ['fajr', 'dhuhr', 'asr_2', 'magrib', 'isha']
    for day in prayer_times_json:
        for prayer in prayer_times_json[day]:
            if prayer in prayers:
                prayer_time = prayer_times_json[day][prayer]
                create_calendar_event(day, prayer_time, prayer, creds)
