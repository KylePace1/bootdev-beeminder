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

def get_xp_from_bootdev():
    """Try to scrape XP from Boot.dev profile"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching {BOOTDEV_URL}...")
        response = requests.get(BOOTDEV_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Search for XP in the HTML
        # Look for patterns like "1234 XP" or similar
        text = soup.get_text()

        # Try to find XP value with regex
        # Look for patterns that specifically match XP (not level)
        # The page likely shows "Level 14" and "960 XP" separately,
        # but they might be concatenated in text as "14960"
        # We want to find the number immediately before "XP"

        # First, try to find a number directly before "XP" (with optional whitespace)
        # Use word boundary to avoid matching partial numbers
        xp_match = re.search(r'(\d+)\s*XP', text, re.IGNORECASE)
        if xp_match:
            xp_str = xp_match.group(1)
            xp = int(xp_str)

            # If the number is > 10000, it likely has level concatenated
            # Boot.dev shows "Level 14" and "960 XP" but they get concatenated as "14960"
            # Extract just the XP portion (last 3-4 digits)
            if xp > 10000:
                # Assume level is 1-2 digits, XP is typically 3 digits (until reaching 1000)
                # Strategy: extract last 3 digits, unless that gives us < 100, then use 4 digits
                xp_3_digits = xp % 1000  # 14960 -> 960
                xp_4_digits = xp % 10000  # 14960 -> 4960

                # If 3-digit extraction gives a reasonable XP value (100-999), use it
                # Otherwise use 4 digits (covers XP >= 1000)
                if xp_3_digits >= 100:
                    xp = xp_3_digits
                else:
                    xp = xp_4_digits
                print(f"Found concatenated value, extracted XP: {xp}")
            else:
                print(f"Found XP: {xp}")
            return xp

        # Fallback patterns
        xp_patterns = [
            r'XP[:\s]*(\d+)',
            r'"xp"[:\s]*(\d+)',
            r'experience[:\s]*(\d+)',
        ]

        for pattern in xp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                xp = int(match.group(1))
                print(f"Found XP: {xp} (pattern: {pattern})")
                return xp
        
        # If not found in text, try to find in script tags (JavaScript variables)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                for pattern in xp_patterns:
                    match = re.search(pattern, script.string, re.IGNORECASE)
                    if match:
                        xp = int(match.group(1))
                        print(f"Found XP in script: {xp}")
                        return xp
        
        print("Could not find XP value in page")
        return None
        
    except Exception as e:
        print(f"Error fetching Boot.dev page: {e}")
        return None

def get_last_xp_from_beeminder():
    """Get the last XP value from Beeminder datapoint comments"""

    if not BEEMINDER_AUTH_TOKEN:
        return None

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
                last_comment = sorted_datapoints[0].get('comment', '')
                print(f"Most recent comment: '{last_comment}'")
                # Extract XP from comment like "Current XP: 960"
                match = re.search(r'Current XP:\s*(\d+)', last_comment)
                if match:
                    last_xp = int(match.group(1))
                    print(f"Last recorded XP: {last_xp}")
                    return last_xp
                else:
                    print("Could not parse XP from comment format")
        else:
            print(f"API error: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"Error fetching last datapoint: {e}")
        return None

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

def main():
    print(f"=== Boot.dev XP Tracker ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Get current XP from Boot.dev
    current_xp = get_xp_from_bootdev()

    if current_xp is None:
        print("\n⚠ Failed to retrieve XP value")
        print("Could not fetch XP from Boot.dev profile.")
        sys.exit(1)

    print(f"\nCurrent XP: {current_xp}")

    # Get last recorded XP from Beeminder
    last_xp = get_last_xp_from_beeminder()

    if last_xp is None:
        print("No previous datapoint found - posting initial value")
        post_to_beeminder(1, comment=f"Current XP: {current_xp}")
    elif current_xp > last_xp:
        xp_gained = current_xp - last_xp
        print(f"✓ XP increased by {xp_gained}! ({last_xp} → {current_xp})")
        post_to_beeminder(1, comment=f"Current XP: {current_xp} (+{xp_gained})")
    else:
        print(f"✗ No XP gained since last check (still at {current_xp})")
        print("Skipping Beeminder update - no work done today")

if __name__ == "__main__":
    main()
