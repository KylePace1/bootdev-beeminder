## Repo: Boot.dev → Beeminder (cat-gif-generator workspace)

This repository contains two small Python scripts that scrape XP from a Boot.dev profile and post it to a Beeminder goal.
The goal of these instructions is to help an AI coding agent become productive quickly in this codebase by documenting the architecture, workflows, conventions, and concrete edit examples.

### Big picture
- Two runnable entry points:
  - `bootdev_beeminder_simple.py` — preferred first attempt. Uses `requests` + `BeautifulSoup` to scrape static HTML.
  - `bootdev_beeminder.py` — fallback using Selenium/ChromeDriver for JS-rendered pages.
- Both scripts: fetch Boot.dev profile, extract an XP integer, then call Beeminder API (`post_to_beeminder`).
- Config/configurable bits live at the top of each script:
  - `BOOTDEV_URL`, `BEEMINDER_USERNAME`, `BEEMINDER_GOAL`, `BEEMINDER_AUTH_TOKEN` (reads from env var `BEEMINDER_TOKEN`).

### Key files to inspect
- `README.md` — contains install, usage, cron and GitHub Actions examples. Always check it first for expected developer workflows.
- `bootdev_beeminder_simple.py` — faster and simpler; try this before Selenium.
- `bootdev_beeminder.py` — headless Chrome usage, includes XPath fallbacks and debug page-source printing.
- `requirements.txt` — install dependencies (used in README). Keep this file in sync with any added packages.

### Developer workflows & commands
- Install deps: `pip install -r requirements.txt` (see README)
- Run simple scraper (fast): `python3 bootdev_beeminder_simple.py`
- Run Selenium scraper (needs Chrome/Chromedriver): `python3 bootdev_beeminder.py`
- Manual unit-ish checks described in README:
  - `python3 -c "from bootdev_beeminder_simple import get_xp_from_bootdev; print(get_xp_from_bootdev())"`
  - `python3 -c "from bootdev_beeminder_simple import post_to_beeminder; post_to_beeminder(1234, 'test')"`
- Automation examples (already in README): cron examples and a sample GitHub Actions workflow that runs `bootdev_beeminder_simple.py`.

### Project-specific conventions & patterns
- Prefer the simple scraper when possible. The codebase expects you to try `bootdev_beeminder_simple.py` first and only use Selenium when the XP is JS-rendered.
- Environment secrets are passed via `BEEMINDER_TOKEN` env var. NEVER hard-code tokens — update README or Action secrets only.
- The scraping logic is tolerant: both scripts use regex patterns to extract the first integer-looking XP. If you change selectors, update both scripts for consistency.
- Exit codes: scripts call `sys.exit(1)` on failure — CI/cron relies on exit status.

### Integration points & failure modes to watch for
- Beeminder API: `POST https://www.beeminder.com/api/v1/users/{user}/goals/{goal}/datapoints.json` — success currently assumed when status_code == 200.
  - If API semantics change, update `post_to_beeminder` to handle other 2xx codes and error payloads.
- Boot.dev rendering: if the XP is rendered client-side, `bootdev_beeminder_simple.py` will fail and instruct to use the Selenium script.
- Selenium requirements on macOS: Homebrew `chromedriver` or system ChromeDriver must match Chrome/Chromium version. README includes install hints.

### Concrete examples for common agent tasks
- Update selector in simple scraper:
  - Open `bootdev_beeminder_simple.py` and search for `xp_patterns` (regexes near top of `get_xp_from_bootdev`). Add or change patterns to match the profile HTML.
- Add a new user-configurable option:
  - Add a small `config.py` if you need more runtime config (example: `USE_SELENIUM = False`) and import it from both scripts.
- Improve Beeminder error handling:
  - Edit `post_to_beeminder` in both scripts to log `response.json()` on non-200 and to treat 201/202 as success if necessary.

### Minimal “contract” for changes an agent may make
- Inputs: profile URL (`BOOTDEV_URL`), env `BEEMINDER_TOKEN`, `BEEMINDER_USERNAME`, `BEEMINDER_GOAL`.
- Outputs: integer XP sent to Beeminder via API, exit code 0 on success, 1 on failure.
- Error modes: network errors fetching profile, XP not found, invalid/missing token, API non-200 responses.

### Quick checklist before submitting changes
1. Run `python3 bootdev_beeminder_simple.py` locally (with `BEEMINDER_TOKEN` set to a test token) to confirm no regressions.
2. If you change scraping, run the manual `-c` tests from the README to validate extraction and posting.
3. Do not commit any secrets. If adding CI, instruct users to add `BEEMINDER_TOKEN` to repo secrets.

### Where this file came from
Based on the current `README.md`, `bootdev_beeminder_simple.py`, and `bootdev_beeminder.py` files in the repository. If you have project-specific CI, tests, or new integration points, add them here so agents can discover them automatically.

If anything is unclear or you'd like more/less detail (for example: specific examples of XPath or the exact ChromeDriver/version steps on macOS), tell me which area to expand and I will iterate.
