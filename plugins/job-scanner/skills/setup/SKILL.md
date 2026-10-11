---
name: setup
description: >
  This skill should be used when the user wants to "set up Job Scanner", "set up my job search",
  "start the job scanner", "onboard me", "create my job dashboard", or installs the job-scanner
  plugin for the first time. It interviews the user, builds their personal settings, publishes
  their own job dashboard, and schedules the twice-daily scan and the hourly outreach worker.
metadata:
  version: "0.1.0"
---

# Job Scanner setup

Set up a personal job search engine for the user: a private dashboard (an Artifact with a database), their settings stored in that database, and two scheduled routines that scan job boards, score postings against their resume, and draft outreach emails in Gmail. Nothing is ever sent or applied to automatically.

Privacy rule: the user's answers go ONLY into their own dashboard database (`engine/config`). Never write them into the plugin folder, a repo, or any file that could be shared.

Bundled files (paths relative to this plugin's root, two levels above this SKILL.md):
- `assets/dashboard.html`: the dashboard page.
- `references/runbook.md`: the run procedure copied into the user's database.
- `references/config-schema.md`: every config field. Read it before building the config.
- `references/routine-prompts.md`: the two routine prompts.
- `scripts/scan.py`: the job board scanner.
- `examples/config.example.json`: a complete example config for a fictional user.

## 1. Check what is connected

Confirm these are available and tell the user plainly what is missing and how to connect it (they can continue without the optional ones):
- ArtifactData and Artifact tools (required).
- Gmail connector (required for drafts and the application tracker).
- Google Drive connector (only if the resume is a Google Doc).
- Claude in Chrome (needed for Apollo email lookups and the optional Simplify/Handshake/Wellfound scans; the user's computer must be on with Chrome open when routines run).
- A way to create scheduled routines (the `schedule` skill / routines, or Cowork scheduled tasks).
- An Apollo account (free plan works: about 10 verified email reveals a day). Optional; without it, outreach records LinkedIn notes instead of emails.

## 2. Interview

Ask in small groups (use AskUserQuestion when available; otherwise ask in plain chat). Prefer offering choices over open questions. Collect:
1. First name and timezone (infer the timezone from their city, confirm it).
2. Target roles: what jobs they want, in their words. Turn that into 2-5 `tracks` (name + description listing concrete role titles) and ask which one is the priority. Derive `queries` (5-15 short search terms) from the tracks.
3. Level: graduation date, years of experience, the max years a posting can ask for.
4. Locations: countries, cities, remote OK?
5. Work authorization: citizenship/visa situation in their words. Turn it into `summary`, `hard_no` and `risky`.
6. Internships: include them? which seasons? keep "students only" ones and flag them?
7. Companies to never show (and why).
8. Resume: a Google Doc link (store the doc id) or pasted text (store in `engine/resume`). Read it once to confirm access and to sanity-check the tracks against it.
9. Sources: which of Simplify, Handshake and Wellfound they are signed in to in Chrome (each is optional and off by default).
10. Outreach: on or off; Apollo connected in Chrome; daily reveal cap (default 10).
11. Email voice: tone preference, 3-5 real achievements for the "What I'd bring" bullets (use their resume to suggest them, but they must confirm every one is true), the sign-off name, and links (portfolio, LinkedIn). Never invent achievements.
12. Schedule: scan times (default 7:00 AM and 5:00 PM local, weekdays) and the worker minute (default :20).

## 3. Build the watchlist

Suggest 30-60 companies that hire for their tracks and locations and post jobs on Ashby, Greenhouse, Lever or SmartRecruiters (`[ats, slug]` pairs; the slug is the company's board name, e.g. `boards.greenhouse.io/<slug>`). Add any companies the user names. Then verify:
- Write the draft config to a temporary file, write `scripts/scan.py` next to it, run `python3 scan.py --check config.json`, and drop or fix every FAIL line.
Tell the user the watchlist is editable later.

## 4. Confirm

Show a short, plain-language summary of the settings (tracks, locations, authorization rules, thresholds, sources, outreach, schedule). Apply their corrections. Defaults when unsure: dashboard_min_score 4.0, outreach_min_score 4.5, drafts_per_run 12, tracker on.

## 5. Publish the dashboard

- Copy `assets/dashboard.html` to a working file (scratchpad or working directory).
- Publish it with the Artifact tool as a new artifact with `capabilities: {"db": {}}` (load the `artifact-capabilities` skill first if the environment asks for it), icon "briefcase", title "<First name>'s Job Scanner". Keep the returned URL: it is the user's dashboard and database.

## 6. Write the database

One ArtifactData `batch` on the new dashboard URL:
- `engine/config`: the full config (shape in references/config-schema.md, `version: 1`).
- `engine/runbook`: `{text: <contents of references/runbook.md>, plugin_version: <plugin version>}`.
- `engine/scan_py`: `{code: <contents of scripts/scan.py>, plugin_version: <plugin version>}`.
- `engine/resume`: `{text}` only if the resume was pasted.
- `meta/status`: `{current_run: null, updated_at: now}`.

## 7. Schedule the routines

Create both routines from `references/routine-prompts.md`, filling in the dashboard URL and first name, and converting the local scan times to the scheduler's timezone (claude.ai routines use UTC cron). Enable the Gmail, Google Drive (if used) and Claude in Chrome connectors on both. Relay each routine's link and next run time to the user. If no scheduling tool is available, give the user the two prompts and cron schedules to paste into their scheduler.

## 8. Finish

- Offer to run the first pass now (the `run` skill).
- Tell the user, briefly: keep the computer on with Chrome open and signed in to Apollo (and any optional job sites) during run times; drafts appear in Gmail and on the dashboard's Today tab; nothing is ever sent or applied to without them; change settings any time by asking to "change my job scanner settings".
