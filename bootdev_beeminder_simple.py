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

        # Find level - look for "Level X" pattern
        level_match = re.search(r'Level\s+(\d+)', text, re.IGNORECASE)
        level = int(level_match.group(1)) if level_match else None

        # Find XP - look for "X XP" pattern
        xp_match = re.search(r'(\d+)\s*XP', text, re.IGNORECASE)
        xp_raw = int(xp_match.group(1)) if xp_match else None

        if level is not None and xp_raw is not None:
            # The page concatenates level + XP (e.g., "14" + "4960" = "144960")
            # We need to extract just the XP portion
            # Strategy: convert both to strings and remove level prefix
            level_str = str(level)
            xp_raw_str = str(xp_raw)

            # If the raw value starts with the level, strip it
            if xp_raw_str.startswith(level_str) and len(xp_raw_str) > len(level_str):
                xp_str = xp_raw_str[len(level_str):]
                xp = int(xp_str)
            else:
                # If not concatenated, use raw value
                xp = xp_raw

            print(f"Found Level: {level}, XP: {xp}")
            return (level, xp)

        # Fallback: try to find them in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                if level is None:
                    level_match = re.search(r'"level"[:\s]*(\d+)', script.string, re.IGNORECASE)
                    if level_match:
                        level = int(level_match.group(1))

                if xp_raw is None:
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
