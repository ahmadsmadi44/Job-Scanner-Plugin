# Job Scanner

A personal job search engine that runs inside Claude. Twice a day it scans job boards for new postings, screens and scores each one against your resume, finds the hiring manager's verified email, and leaves a personal outreach draft in your Gmail. You review everything on a live dashboard, and **nothing is ever sent or applied to without you.**

## What it does

| Step | What happens |
|---|---|
| Scan | Polls company job boards (Ashby, Greenhouse, Lever, SmartRecruiters) and Simplify's public new-grad and internship lists. Optional: Simplify's website, Handshake and Wellfound in your own signed-in Chrome. |
| Screen | Claude keeps only roles that fit your target tracks, locations and seniority, and logs every drop with a reason. |
| Read | Opens each posting, checks it's still live, and applies your hard filters (years of experience, work authorization, grad year). |
| Score | Scores 1-5 against your resume, with a concrete "why it fits" and watch-outs. |
| Outreach | For top matches (or any job you click "Draft email" on), finds the hiring manager or recruiter, gets a verified email from your Apollo account, and writes a short, personal draft in your voice. |
| Tracker | Each morning, reads your Gmail for application receipts, rejections and interview invites and keeps an application tracker. |

Everything shows up on your own private dashboard: today's emails to send, new matches, every job scored, your outreach, applications, and a live log of every run.

## What you need

- A paid Claude plan with routines (scheduled tasks)
- Connectors: **Gmail** (required), **Google Drive** (if your resume is a Google Doc)
- **Claude in Chrome**, with your computer on and Chrome open at run times (for Apollo lookups and the optional browser sources)
- An **Apollo** account (the free plan gives about 10 verified email reveals a day). Optional: without it you get LinkedIn notes instead of emails.

## Install

In Claude Code or Cowork:

```
/plugin marketplace add ahmadsmadi44/job-scanner-plugin
/plugin install job-scanner@job-scanner
```

Then say **"set up Job Scanner"**. Setup takes about 10 minutes. It asks what jobs you want, where, your work authorization, your resume and how you like to write, then builds your dashboard and schedules everything.

## Using it

- **"run the job scanner"**: run a pass right now
- **"draft my queued emails"**: process the "Draft email" clicks right away instead of waiting for the hourly worker
- **"change my job scanner settings"**: add tracks or companies, change your email voice, thresholds or run times
- **"update the job scanner"**: after a plugin update, pull the latest engine into your dashboard

## Privacy

Your settings, resume, jobs and outreach live only in your own private dashboard's database, under your own Claude account. This repository contains no personal data, and setup never writes your answers into the plugin files. The plugin never stores passwords, never solves CAPTCHAs, never sends email and never submits applications.

## Be a good citizen

Outreach drafts go to real people. Keep them few, personal and true: the plugin only uses achievements you confirm, caps drafts per run, and never contacts the same person twice. Respect each site's terms: browser sources are read-only and run in your own signed-in browser at a human pace.

## How it's built

```
plugins/job-scanner/
├── .claude-plugin/plugin.json
├── skills/
│   ├── setup/      onboarding, dashboard, routines
│   ├── run/        run a pass on demand
│   └── settings/   change settings, sync engine updates
├── references/
│   ├── runbook.md          the full run procedure
│   ├── routine-prompts.md  the two scheduled routines
│   └── config-schema.md    every setting
├── scripts/scan.py         zero-cost job board scanner
├── assets/dashboard.html   the dashboard
└── examples/config.example.json
```

The scheduled routines read the procedure from your dashboard's database, so a plugin update reaches your routines once you say "update the job scanner".

## License

MIT
