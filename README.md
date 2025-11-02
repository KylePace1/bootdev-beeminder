# Boot.dev XP Tracker for Beeminder

Automatically track your Boot.dev study sessions to Beeminder using GitHub Actions. Runs daily at midnight PST and posts a "1" to your Beeminder goal (indicating you studied) with your current XP as a comment.

## Quick Setup

### 1. Fork or Clone This Repository

```bash
git clone https://github.com/KylePace1/bootdev-beeminder.git
cd bootdev-beeminder
```

### 2. Configure Your Settings

Edit `bootdev_beeminder_simple.py` and update these lines:

```python
BOOTDEV_URL = "https://www.boot.dev/u/YOUR_USERNAME"  # Your Boot.dev profile
BEEMINDER_USERNAME = "your_username"  # Your Beeminder username
BEEMINDER_GOAL = "your_goal"  # Your Beeminder goal name
```

### 3. Get Your Beeminder Auth Token

1. Log into [Beeminder](https://www.beeminder.com)
2. Go to https://www.beeminder.com/settings/account
3. Find your "Personal Auth Token"
4. Copy it (you'll need it in the next step)

### 4. Add GitHub Repository Secret

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `BEEMINDER_TOKEN`
5. Value: Paste your Beeminder auth token
6. Click **Add secret**

### 5. Create Your Beeminder Goal

1. Create a new goal on [Beeminder](https://www.beeminder.com)
2. Name it to match what you set in step 2 (e.g., "programming")
3. Set type to **"Do More"**
4. Configure your rate (e.g., 5 days/week = 0.71/day)

### 6. Push to GitHub

```bash
git add bootdev_beeminder_simple.py
git commit -m "Configure settings for my account"
git push
```

That's it! The workflow will automatically run every day at midnight PST.

## How It Works

- **Schedule**: Runs daily at midnight PST (8 AM UTC)
- **What it tracks**: Posts a value of `1` to Beeminder (indicating you studied that day)
- **Comment**: Includes your current Boot.dev XP in the comment
- **Manual trigger**: You can also manually trigger the workflow from the Actions tab

## Testing

To test the workflow manually:

1. Go to the **Actions** tab in your GitHub repository
2. Click on **"Track Boot.dev XP"**
3. Click **"Run workflow"**
4. Check the logs to verify it's working correctly

## Changing the Schedule

Edit [.github/workflows/track.yml](.github/workflows/track.yml) and modify the cron expression:

```yaml
schedule:
  - cron: '0 8 * * *'  # Daily at midnight PST (8 AM UTC)
```

Common schedules:
- `'0 8 * * *'` - Daily at midnight PST
- `'0 */12 * * *'` - Every 12 hours
- `'0 0 * * 1,3,5'` - Mondays, Wednesdays, and Fridays at midnight UTC

## Troubleshooting

### Workflow Fails

Check the Actions tab for error logs. Common issues:
- `BEEMINDER_TOKEN` secret not set correctly
- Incorrect username or goal name in the script
- Boot.dev profile is private or URL changed

### XP Not Parsing Correctly

The script handles Boot.dev's concatenated level + XP display (e.g., "Level 14" + "960 XP" = "14960"). If you see incorrect values:

1. Run the workflow manually and check logs
2. Verify the XP extraction logic in `bootdev_beeminder_simple.py`

### Test Locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
export BEEMINDER_TOKEN='your_token_here'
python3 bootdev_beeminder_simple.py
```

## Project Structure

```
.
├── .github/workflows/track.yml    # GitHub Actions workflow
├── bootdev_beeminder_simple.py    # Main tracking script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Tips

- This tracks **days studied** (binary: yes/no), not cumulative XP
- Perfect for accountability and building a study habit
- Your XP is logged in the comment for reference
- Free to run - GitHub Actions provides free minutes for public repos

## License

MIT

Good luck with your learning goals! 🚀
