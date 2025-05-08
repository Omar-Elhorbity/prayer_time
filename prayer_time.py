#!/usr/bin/env python3
from datetime import datetime, timedelta
import requests
import os
import json
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
CYAN = "\033[36m"

def convert_time(time_24):
    try:
        hours, minutes = map(int, time_24.split(":"))
        if not (0 <= hours <= 23) or not (0 <= minutes <= 59):
            raise ValueError("Invalid time")

        period = "AM" if hours < 12 else "PM"
        hours = hours % 12
        hours = 12 if hours == 0 else hours
        return f"{hours}:{minutes:02d} {period}"
    except Exception as e:
        return f"Error: {e}"

def fetch_location():
    """
    Fetch location using multiple services for better accuracy
    Returns: country, city
    """
    # First, try to read saved location
    try:
        with open(os.path.expanduser('~/.prayer_location'), 'r') as f:
            saved_location = json.load(f)
            return saved_location['country'], saved_location['city']
    except Exception:
        pass

    def get_manual_location():
        print("\nEnter your location manually:")
        country = input("Country (e.g., Egypt): ").strip()
        city = input("City (e.g., Fuwwah): ").strip()
        
        # Save the manual input for future use
        try:
            with open(os.path.expanduser('~/.prayer_location'), 'w') as f:
                json.dump({'country': country, 'city': city}, f)
        except Exception:
            pass
        
        return country, city

    # Check if force manual input is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        return get_manual_location()

    def try_ipapi():
        try:
            r = requests.get('http://ip-api.com/json/', timeout=5)
            data = r.json()
            if data.get('status') == 'success':
                print("\nAutomatic location detection might not be accurate.")
                print(f"Detected: {data.get('city')}, {data.get('country')}")
                choice = input("Use this location? (y/n): ").strip().lower()
                if choice != 'y':
                    return get_manual_location()
                return data.get('country'), data.get('city')
        except Exception:
            return None, None

    def try_ipinfo():
        try:
            r = requests.get('https://ipinfo.io/json', timeout=5)
            data = r.json()
            if 'country' in data and 'city' in data:
                print("\nAutomatic location detection might not be accurate.")
                print(f"Detected: {data.get('city')}, {data.get('country')}")
                choice = input("Use this location? (y/n): ").strip().lower()
                if choice != 'y':
                    return get_manual_location()
                return data.get('country'), data.get('city')
        except Exception:
            return None, None

    # Try each service in order until we get a valid response
    for service in [try_ipapi, try_ipinfo]:
        country, city = service()
        if country and city:
            return country, city

    # If all services fail, ask for manual input
    print("\nCould not automatically determine your location.")
    return get_manual_location()

def fetch_ptimes(country, city):
    try:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        URL = f"https://api.aladhan.com/v1/timingsByCity/{day}-{month}-{year}?city={city}&country={country}"
        r = requests.get(URL, timeout=5)
        return r.json()['data']
    except Exception as e:
        print(f"Error fetching prayer times: {e}")
        return None

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except:
        return

def convert_to_datetime(time_str):
    """Convert prayer time string to datetime object"""
    now = datetime.now()
    hour, minute = map(int, time_str.split(':'))
    prayer_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if prayer_time < now and hour < 12:
        prayer_time += timedelta(days=1)

    return prayer_time

def time_until_next_prayer(prayer_times):
    """Calculate time until the next prayer"""
    now = datetime.now()

    prayers = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    prayer_datetimes = {}

    for prayer in prayers:
        if prayer in prayer_times:
            prayer_datetimes[prayer] = convert_to_datetime(prayer_times[prayer])

    next_prayer = None
    min_diff = timedelta(days=1)

    for prayer, prayer_time in prayer_datetimes.items():
        diff = prayer_time - now
        if diff > timedelta(0) and diff < min_diff:
            min_diff = diff
            next_prayer = prayer

    if next_prayer is None:
        next_prayer = 'Fajr'
        fajr_time = convert_to_datetime(prayer_times['Fajr'])
        min_diff = (fajr_time + timedelta(days=1)) - now

    hours, remainder = divmod(min_diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return next_prayer, f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display():
    width = get_terminal_width()
    divider = "─" * width

    country, city = fetch_location()
    if not country or not city:
        print("Could not determine your location")
        return

    data = fetch_ptimes(country, city)
    if not data:
        print("Could not fetch prayer times")
        return

    next_prayer, time_left = time_until_next_prayer(data['timings'])

    print(f"{BLUE}{divider}{RESET}")
    print(f"🕌 {BOLD}Prayer Times for {city}, {country}{RESET} 🕌")

    gregorian = data['date']['readable']
    hijri = f"{data['date']['hijri']['date']} ({data['date']['hijri']['month']['en']})"
    print(f"{BLUE}{divider}{RESET}")
    print(f"Date: {gregorian} | Hijri: {hijri}")

    print(f"{BLUE}{divider}{RESET}")
    print(f"{CYAN}{BOLD}Next Prayer: {next_prayer} in {time_left}{RESET}")

    print(f"{BLUE}{divider}{RESET}")
    print(f"{BOLD}Prayer Times:{RESET}")

    prayers = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    max_name_len = max(len(name) for name in prayers)

    for prayer in prayers:
        if prayer in data['timings']:
            time = data['timings'][prayer]
            name_padded = prayer.ljust(max_name_len)

            if prayer == next_prayer:
                print(f"🕌 {CYAN}{BOLD}{name_padded}{RESET}: {CYAN}{convert_time(time)} ← Next{RESET}")
            elif prayer in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                print(f"📿 {GREEN}{BOLD}{name_padded}{RESET}: {YELLOW}{convert_time(time)}{RESET}")

    print(f"{BLUE}{divider}{RESET}")

if __name__ == "__main__":
    display()
