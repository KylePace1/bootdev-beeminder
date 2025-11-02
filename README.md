# Boot.dev XP Tracker for Beeminder

Track your Boot.dev XP automatically and send it to Beeminder!

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For the Selenium version, you'll also need Chrome/Chromium and ChromeDriver:
```bash
# On Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# On macOS with Homebrew
brew install chromedriver
```

### 2. Get Your Beeminder Auth Token

1. Log into Beeminder
2. Go to https://www.beeminder.com/settings/account
3. Find your "Personal Auth Token"
4. Copy it

### 3. Create a Beeminder Goal

1. Create a new goal on Beeminder (e.g., "bootdev_xp")
2. Set it to "Do More" type
3. Configure your yellow brick road

### 4. Configure the Script

Edit either `bootdev_beeminder_simple.py` or `bootdev_beeminder.py`:

```python
BEEMINDER_USERNAME = "your_username"  # Your Beeminder username
BEEMINDER_GOAL = "bootdev_xp"  # Your goal name
```

### 5. Set Your Auth Token

```bash
export BEEMINDER_TOKEN='your_token_here'
```

Or add it to your `.bashrc` or `.zshrc`:
```bash
echo 'export BEEMINDER_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Try the Simple Version First

```bash
python3 bootdev_beeminder_simple.py
```

This uses requests and BeautifulSoup. If Boot.dev's XP is visible in the HTML, this will work great!

### If That Doesn't Work, Use Selenium

```bash
python3 bootdev_beeminder.py
```

This uses a headless browser to handle JavaScript-rendered content.

## Automating with Cron

To run this automatically every day at 9 PM:

```bash
crontab -e
```

Add this line:
```
0 21 * * * cd /path/to/script && /usr/bin/python3 bootdev_beeminder_simple.py >> /tmp/bootdev_tracker.log 2>&1
```

Or for multiple times per day (every 6 hours):
```
0 */6 * * * cd /path/to/script && /usr/bin/python3 bootdev_beeminder_simple.py >> /tmp/bootdev_tracker.log 2>&1
```

## Troubleshooting

### Can't Find XP Value

Boot.dev might be rendering the XP with JavaScript. Try:

1. Open https://www.boot.dev/u/kylepace in your browser
2. Right-click on the XP number and select "Inspect"
3. Look at the HTML element and its classes/IDs
4. Update the script's selectors to match

Example:
```python
# If the XP is in a span with class "xp-value"
xp_element = soup.find('span', class_='xp-value')
```

### Beeminder API Errors

- Make sure your auth token is correct
- Verify your username and goal name are spelled correctly
- Check that the goal exists and accepts manual data entry

### Manual Testing

Test just the scraping part:
```python
python3 -c "from bootdev_beeminder_simple import get_xp_from_bootdev; print(get_xp_from_bootdev())"
```

Test just the Beeminder posting:
```python
python3 -c "from bootdev_beeminder_simple import post_to_beeminder; post_to_beeminder(1234, 'test')"
```

## Advanced: Using GitHub Actions

You can also run this in the cloud with GitHub Actions for free:

1. Create a new GitHub repository
2. Add these files to it
3. Add your `BEEMINDER_TOKEN` as a repository secret
4. Create `.github/workflows/track.yml`:

```yaml
name: Track Boot.dev XP
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python bootdev_beeminder_simple.py
        env:
          BEEMINDER_TOKEN: ${{ secrets.BEEMINDER_TOKEN }}
```

## Tips

- Start with cumulative tracking (total XP) rather than daily XP
- Set a reasonable goal rate based on your learning pace
- Consider tracking "days studied" instead if XP growth is irregular
- Use Beeminder's "odometer" feature if you want to track total XP

Good luck with your learning goals! 🚀
