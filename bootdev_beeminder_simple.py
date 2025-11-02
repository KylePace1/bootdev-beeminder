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
        xp_patterns = [
            r'(\d+)\s*XP',
            r'XP[:\s]*(\d+)',
            r'"xp"[:\s]*(\d+)',
            r'experience[:\s]*(\d+)',
        ]
        
        for pattern in xp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                xp = int(match.group(1))
                print(f"Found XP: {xp}")
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
        print(f"Posting to Beeminder: {value} XP")
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✓ Successfully posted {value} XP to Beeminder")
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
    
    xp = get_xp_from_bootdev()
    
    if xp is not None:
        print(f"\nCurrent XP: {xp}")
        post_to_beeminder(xp, comment="Auto-tracked from Boot.dev")
    else:
        print("\n⚠ Failed to retrieve XP value")
        print("The page might be JavaScript-rendered. Try using the Selenium version instead.")
        sys.exit(1)

if __name__ == "__main__":
    main()
