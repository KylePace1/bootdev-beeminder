#!/usr/bin/env python3
"""
Boot.dev XP Tracker for Beeminder (Simple Version)
Uses requests and BeautifulSoup for faster execution
"""

import os
import sys
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuration
BOOTDEV_URL = "https://www.boot.dev/u/kylepace"
BEEMINDER_USERNAME = "kyle"  # Replace with your Beeminder username
BEEMINDER_GOAL = "programming"  # Replace with your goal name
BEEMINDER_AUTH_TOKEN = os.environ.get("BEEMINDER_TOKEN")  # Set as environment variable

def get_level_and_xp_from_bootdev():
    """Scrape both level and XP from Boot.dev profile, return as tuple (level, xp)"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        print(f"Fetching {BOOTDEV_URL}...")
        response = requests.get(BOOTDEV_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # The page shows: "Level 14,132 XP" or "Level 141,132 XP"
        # Pattern: Level [digits with optional commas] XP
        pattern = r'Level\s+([\d,]+)\s*XP'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            # Extract the full number string (e.g., "141,132")
            raw_match = match.group(1)
            full_number = raw_match.replace(',', '')  # Remove commas: "141132"

            # The number is concatenated: first 1-2 digits are level, rest is XP
            # Strategy: try 2-digit level first, then 1-digit
            if len(full_number) >= 4:  # Minimum: "1100" (level 1, xp 100)
                # Try 2-digit level first
                if len(full_number) >= 5:  # e.g., "141132" = level 14, xp 1132
                    level = int(full_number[:2])
                    xp = int(full_number[2:])
                else:  # e.g., "1132" = level 1, xp 132
                    level = int(full_number[0])
                    xp = int(full_number[1:])

                print(f"Found Level: {level}, XP: {xp} (from '{raw_match}')")
                return (level, xp)

        print("Could not parse level and XP from text")
        level = None
        xp = None

        # Fallback: try to find them in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                if level is None:
                    level_match = re.search(r'"level"[:\s]*(\d+)', script.string, re.IGNORECASE)
                    if level_match:
                        level = int(level_match.group(1))

                if xp is None:
                    xp_match = re.search(r'"xp"[:\s]*(\d+)', script.string, re.IGNORECASE)
                    if xp_match:
                        xp = int(xp_match.group(1))

                if level is not None and xp is not None:
                    print(f"Found in script - Level: {level}, XP: {xp}")
                    return (level, xp)

        print("Could not find level and XP values in page")
        return (None, None)

    except Exception as e:
        print(f"Error fetching Boot.dev page: {e}")
        return (None, None)

def get_last_progress_from_beeminder():
    """Get the last level and XP from Beeminder datapoint comments"""

    if not BEEMINDER_AUTH_TOKEN:
        return (None, None)

    url = f"https://www.beeminder.com/api/v1/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"

    try:
        # Get all recent datapoints and sort by timestamp to find the most recent
        response = requests.get(url, params={'auth_token': BEEMINDER_AUTH_TOKEN})

        print(f"Beeminder API status: {response.status_code}")

        if response.status_code == 200:
            datapoints = response.json()
            print(f"Found {len(datapoints)} datapoint(s)")
            if datapoints and len(datapoints) > 0:
                # Sort by timestamp descending to get most recent
                sorted_datapoints = sorted(datapoints, key=lambda x: x.get('timestamp', 0), reverse=True)

                # Find the first datapoint with our comment format
                for datapoint in sorted_datapoints:
                    comment = datapoint.get('comment', '')
                    # Extract level and XP from comment like "Level 14, XP: 960"
                    match = re.search(r'Level\s+(\d+),\s*XP:\s*(\d+)', comment)
                    if match:
                        last_level = int(match.group(1))
                        last_xp = int(match.group(2))
                        print(f"Last recorded: Level {last_level}, XP: {last_xp} (from comment: '{comment}')")
                        return (last_level, last_xp)

                print("No datapoint with 'Level X, XP: Y' format found")
        else:
            print(f"API error: {response.text[:200]}")
        return (None, None)
    except Exception as e:
        print(f"Error fetching last datapoint: {e}")
        return (None, None)

def post_to_beeminder(value, comment=None):
    """Post datapoint to Beeminder"""

    if not BEEMINDER_AUTH_TOKEN:
        print("Error: BEEMINDER_TOKEN environment variable not set")
        print("Set it with: export BEEMINDER_TOKEN='your_token_here'")
        sys.exit(1)

    url = f"https://www.beeminder.com/api/v1/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"

    data = {
        'auth_token': BEEMINDER_AUTH_TOKEN,
        'value': value,
        'timestamp': int(time.time()),
    }

    if comment:
        data['comment'] = comment

    try:
        print(f"Posting to Beeminder: value={value}, comment='{comment}'")
        response = requests.post(url, data=data)

        if response.status_code == 200:
            print(f"✓ Successfully posted to Beeminder")
            return True
        else:
            print(f"✗ Error posting to Beeminder: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error posting to Beeminder: {e}")
        return False

def calculate_total_progress(level, xp):
    """Calculate cumulative progress score: (level * 1000) + xp"""
    return (level * 1000) + xp

def main():
    print(f"=== Boot.dev XP Tracker ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Get current level and XP from Boot.dev
    current_level, current_xp = get_level_and_xp_from_bootdev()

    if current_level is None or current_xp is None:
        print("\n⚠ Failed to retrieve level and XP")
        print("Could not fetch data from Boot.dev profile.")
        sys.exit(1)

    current_total = calculate_total_progress(current_level, current_xp)
    print(f"\nCurrent: Level {current_level}, XP: {current_xp} (Total: {current_total})")

    # Get last recorded level and XP from Beeminder
    last_level, last_xp = get_last_progress_from_beeminder()

    if last_level is None or last_xp is None:
        print("No previous datapoint found - posting initial value")
        post_to_beeminder(1, comment=f"Level {current_level}, XP: {current_xp}")
    else:
        last_total = calculate_total_progress(last_level, last_xp)
        print(f"Last recorded: Level {last_level}, XP: {last_xp} (Total: {last_total})")

        if current_total > last_total:
            progress_gained = current_total - last_total
            print(f"✓ Progress increased by {progress_gained}!")

            # Create descriptive comment
            if current_level > last_level:
                comment = f"Level {current_level}, XP: {current_xp} (leveled up from {last_level}!)"
            else:
                comment = f"Level {current_level}, XP: {current_xp} (+{current_xp - last_xp} XP)"

            post_to_beeminder(1, comment=comment)
        else:
            print(f"✗ No progress since last check")
            print("Skipping Beeminder update - no work done today")

if __name__ == "__main__":
    main()
