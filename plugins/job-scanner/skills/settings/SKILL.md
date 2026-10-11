---
name: settings
description: >
  This skill should be used when the user wants to "change my job scanner settings", "add a track",
  "add companies to my watchlist", "change my email voice", "turn off internships", "change run times",
  "show my job scanner settings", or "update the job scanner" after installing a new plugin version.
  It edits the user's settings in their dashboard database and syncs the latest engine from the plugin.
metadata:
  version: "0.1.0"
---

# Job Scanner settings and updates

Settings live in the user's dashboard database as `engine/config` (fields in `references/config-schema.md`). The plugin's `references/runbook.md` and `scripts/scan.py` are copied into `engine/runbook` and `engine/scan_py` so scheduled routines can read them.

Find the dashboard first: list the user's artifacts and pick the one titled "... Job Scanner" (ask if unclear). Load ArtifactData.

## Show settings
Read `engine/config` and summarise it in plain language (tracks, locations, authorization rules, thresholds, sources, outreach, schedule). Don't dump raw JSON unless asked.

## Change settings
1. Read `engine/config` and note its `version` (the document version, for `if_version`).
2. Make the requested change. Translate plain requests into the right fields, e.g. "also look at product roles" adds a track and queries; "stop showing X" adds to `exclude_companies`; "be more casual" edits `outreach.voice.tone`.
3. For watchlist additions, verify new `[ats, slug]` pairs with `python3 scripts/scan.py --check <tmp config>` before saving.
4. Never put invented achievements into `outreach.voice.achievements`; only facts the user confirms.
5. Write with `update` pinned to the version you read. Confirm the change in one line.
6. If `timezone` or `schedule` changed, update both routines' cron schedules too (see `references/routine-prompts.md`) and relay the new next run times.

## Update the engine (after a plugin update)
1. Read `engine/runbook` and `engine/scan_py` and their `plugin_version`.
2. If the plugin's version (`.claude-plugin/plugin.json`) is newer, `update` both docs with the plugin's current `references/runbook.md` text and `scripts/scan.py` code and the new `plugin_version`.
3. If the plugin's `assets/dashboard.html` changed, republish it to the same dashboard URL (Artifact publish with `url`, after reading the live artifact), keeping `capabilities` unchanged.
4. Check `references/config-schema.md` for new fields; add sensible defaults to `engine/config` and tell the user about anything they may want to set.
5. Never overwrite `engine/config` values the user set.
