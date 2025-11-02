#!/usr/bin/env python3
"""
Boot.dev XP Tracker for Beeminder
Scrapes XP from Boot.dev profile and posts to Beeminder API
"""

import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import time

# Configuration
BOOTDEV_URL = "https://www.boot.dev/u/kylepace"
BEEMINDER_USERNAME = "kyle"  # Replace with your Beeminder username
BEEMINDER_GOAL = "programming"  # Replace with your goal name
BEEMINDER_AUTH_TOKEN = os.environ.get("BEEMINDER_TOKEN")  # Set as environment variable

def get_xp_from_bootdev():
    """Scrape XP value from Boot.dev profile page"""
    
    # Setup Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Fetching {BOOTDEV_URL}...")
        driver.get(BOOTDEV_URL)
        
        # Wait for page to load (adjust selector as needed)
        wait = WebDriverWait(driver, 10)
        
        # Try different possible selectors for XP
        # You'll need to inspect the page to find the exact selector
        possible_selectors = [
            "//span[contains(text(), 'XP')]",
            "//div[contains(@class, 'xp')]",
            "//*[contains(text(), 'XP')]"
        ]
        
        xp_value = None
        
        # Try to find XP element
        for selector in possible_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                text = element.text
                print(f"Found text: {text}")
                
                # Extract number from text (handles formats like "1234 XP" or "XP: 1234")
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    xp_value = int(numbers[0])
                    break
            except:
                continue
        
        if xp_value is None:
            # Fallback: print page source to debug
            print("Could not find XP value. Here's the page content:")
            print(driver.page_source[:1000])  # Print first 1000 chars
            
        return xp_value
        
    finally:
        driver.quit()

def post_to_beeminder(value, comment=None):
    """Post datapoint to Beeminder"""
    
    if not BEEMINDER_AUTH_TOKEN:
        print("Error: BEEMINDER_TOKEN environment variable not set")
        sys.exit(1)
    
    url = f"https://www.beeminder.com/api/v1/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
    
    data = {
        'auth_token': BEEMINDER_AUTH_TOKEN,
        'value': value,
        'timestamp': int(time.time()),
    }
    
    if comment:
        data['comment'] = comment
    
    print(f"Posting to Beeminder: {value} XP")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"✓ Successfully posted {value} XP to Beeminder")
        return True
    else:
        print(f"✗ Error posting to Beeminder: {response.status_code}")
        print(response.text)
        return False

def main():
    print(f"=== Boot.dev XP Tracker ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    xp = get_xp_from_bootdev()
    
    if xp is not None:
        print(f"Current XP: {xp}")
        post_to_beeminder(xp, comment="Auto-tracked from Boot.dev")
    else:
        print("Failed to retrieve XP value")
        sys.exit(1)

if __name__ == "__main__":
    main()
