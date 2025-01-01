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
    return data.get("times")
        

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


def delete_events(credents):
    # Specify the date range for events deletion
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2025, 1, 4, 0, 0, 0)

    service = build('calendar', 'v3', credentials=credents)

    # Get calendar ID by calendar name
    calendar_id = '1a4a4046ea518584fe2a3a0dc2dcffc889427489a999182a13214a1c2c5d830c@group.calendar.google.com'

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

    prayers = ['fajr', 'sunrise', 'dhuhr', 'asr_2', 'magrib', 'isha']
    for day in tqdm(prayer_times_json):
        for prayer in prayer_times_json[day]:
            if prayer in prayers:
                prayer_time = prayer_times_json[day][prayer]
                create_calendar_event(day, prayer_time, prayer, creds)


                # After isha prayer, calculate additional times for midnight and first third
            next_day = (datetime.strptime(day, '%Y-%m-%d').date() + timedelta(days=1)).strftime('%Y-%m-%d')
            if prayer == 'isha':
                if next_day in prayer_times_json:
                    next_fajr = prayer_times_json[next_day].get('fajr')
                elif month == 'december':
                    # Handle end of the year case
                    break
                else:
                    # Move to the next month
                    i = months_list.index(month)
                    next_month = months_list[(i + 1) % 12]
                    if next_month == 'january':
                        year = str(int(year) + 1)
                    next_month_data = get_monthly_prayer_time_data_from_api(year, next_month)
                    if next_month_data and next_day in next_month_data:
                        next_fajr = next_month_data[next_day].get('fajr')
                    else:
                        print(f"Error: Could not retrieve prayer times for {next_day}.")
                        continue  # Skip further processing for this case

                # Calculate midnight and first third times
                if next_fajr:
                    next_fajr = datetime.strptime(next_fajr, '%H:%M')
                    magrib = datetime.strptime(prayer_times_json[day]['magrib'], '%H:%M')
                    if next_fajr < magrib:
                        next_fajr += timedelta(days=1)
                    time_difference = next_fajr - magrib
                    midnight = magrib + (time_difference / 2)
                    first_third = magrib + (time_difference / 3)

                    # Determine correct dates for midnight and first third
                    midnight_day = day if midnight.hour >= 12 else next_day
                    first_third_day = day if first_third.hour >= 12 else next_day

                    # Create calendar events
                    create_calendar_event(midnight_day, midnight.strftime('%H:%M'), 'midnight', creds)
                    create_calendar_event(first_third_day, first_third.strftime('%H:%M'), 'first_third', creds)
    print("Check your calendar at the month and year you inputted. You will find Hornchurch prayer times there.")
