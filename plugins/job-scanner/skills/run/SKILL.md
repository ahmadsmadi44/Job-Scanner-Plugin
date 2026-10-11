---
name: run
description: >
  This skill should be used when the user asks to "run the job scanner", "scan for jobs now",
  "find me new jobs", "run my job pipeline", "do a job scan", or "draft my queued emails" and they
  have already set up Job Scanner. It runs one full pass (scan, screen, read, score, outreach drafts)
  or just the outreach queue, using the user's own dashboard and settings.
metadata:
  version: "0.1.0"
---

# Run Job Scanner now

Run one pass on demand, exactly as the scheduled routine would.

1. Find the user's dashboard: list their artifacts (Artifact tool, `action: "list"`) and pick the one titled "... Job Scanner". If there are several or none, ask the user for the link. If there is none, offer the `setup` skill instead.
2. Load ArtifactData. Read `engine/config` and `engine/runbook`.
3. Compare `engine/runbook.plugin_version` with this plugin's version (`.claude-plugin/plugin.json`). If the plugin is newer, tell the user in one line and offer to update their engine with the `settings` skill first; continue with the database copy if they decline.
4. Decide the scope from the request:
   - "draft my queued emails" / "process the outreach queue": follow only the runbook's OUTREACH PROCEDURE for `outreach_requests` with status "queued" (oldest first, max 10), the same way the hourly worker does.
   - Anything else: a full pass. Follow `engine/runbook` step by step, using run_id `YYYY-MM-DD-manual-HHMM` and slot "manual" instead of am/pm. Run the tracker step only if the user asks or it is a morning run.
5. All hard rules in the runbook apply: never send email, never apply, never type passwords or solve CAPTCHAs, verified Apollo emails only, close every tab opened.
6. Reply with the runbook's 3-line summary and the dashboard link.
