# engine/config schema

The user's settings live in their dashboard database as the doc `engine/config`. Nothing personal belongs in the plugin itself. `examples/config.example.json` is a complete example for a fictional user.

| Field | Type | Meaning |
|---|---|---|
| `version` | int | Config format version (currently 1). |
| `owner_first_name` | string | Used in routine prompts and run summaries. |
| `timezone` | IANA tz | e.g. `America/Chicago`. Run ids, run times and the dashboard clock use it. |
| `schedule.scan_times` | ["HH:MM"] | Local times for the main pass (default `["07:00","17:00"]`). |
| `schedule.weekdays_only` | bool | Main pass on weekdays only. |
| `schedule.worker_minute` | 0-59 | Minute past each hour the outreach worker runs. |
| `profile` | string | Short factual summary: degree, grad date, experience, skills, location. Used for screening and scoring. |
| `locations.countries` | [string] | Countries to keep. |
| `locations.include_remote` | bool | Keep remote roles within those countries. |
| `locations.notes` | string | Free-text preferences (cities, relocation). |
| `work_authorization.summary` | string | Plain description, e.g. "International student on F-1 OPT; will need H-1B sponsorship later". |
| `work_authorization.hard_no` | [string] | Requirements that disqualify a posting (e.g. "US citizenship", "security clearance"). |
| `work_authorization.risky` | [string] | Requirements to keep but flag (e.g. "no sponsorship stated"). |
| `experience.max_years` | number | Years required that is still a normal fit. |
| `experience.stretch_years` | number | Above this, drop. Between max and stretch: keep with a watch-out. |
| `experience.graduation` | "YYYY-MM" | Graduation date. |
| `experience.skip_full_time_for_grad_year` | [string] | Full-time roles that require these grad years are dropped. |
| `tracks` | {name: description} | Job families to look for. The description lists role titles and any scoring guidance. |
| `priority_track` | string | Track name that scores up when the work genuinely fits. |
| `exclude_title_keywords` | [string] | Seniority words that drop a title. |
| `exclude_role_types` | [string] | Role families to drop. |
| `exclude_companies` | [{company, reason}] | Never surface these. |
| `internships.include` | bool | Look for internships at all. |
| `internships.terms` | [string] | Seasons to keep, e.g. `["Winter","Spring","Fall"]`. Empty = all. |
| `internships.ignore_enrollment_requirements` | bool | Keep "students only" internships and flag them instead of dropping. |
| `internships.ask_about_enrollment_in_email` | bool | Internship emails ask whether enrollment is required. |
| `internships.generous_track_fit` | bool | Keep adjacent internships, not only exact track matches. |
| `queries` | [string] | Search terms for Simplify, Handshake and Wellfound. |
| `intern_queries` | [string] | Extra internship-only queries for Simplify. |
| `watchlist` | [[ats, slug]] | Company job boards to poll. ats is `ashby`, `greenhouse`, `lever` or `smartrecruiters`. Check with `python3 scan.py --check config.json`. |
| `sources.*` | bool | `company_boards`, `simplify_newgrad`, `simplify_internships` (no browser); `simplify_site`, `handshake`, `wellfound` (need the user signed in to that site in Chrome). |
| `feeds` | {name: url} | Optional overrides for the Simplify data-file URLs (they change name each season). |
| `resume.source` | "google_doc" or "text" | Where the resume lives. |
| `resume.doc_id` | string | Google Doc id when source is google_doc. With "text", the resume is stored in `engine/resume.text`. |
| `thresholds.dashboard_min_score` | number | Minimum score shown under "New matches". |
| `thresholds.outreach_min_score` | number | Jobs at or above this get an automatic outreach draft. |
| `thresholds.drafts_per_run` | int | Max drafts per main pass. |
| `outreach.enabled` | bool | Turn outreach off entirely. |
| `outreach.email_finder` | "apollo_chrome" / "apollo_api" | How to find verified emails. |
| `outreach.apollo_daily_reveals` | int | Daily cap on Apollo email reveals (free plan: 10). |
| `outreach.contact_order` | [string] | Who to try first. |
| `outreach.voice` | object | greeting, length_words, opener_rotation, tone, bring_header, achievements (real results only), ask, closing, signature_name, links [{text,url}], never [phrases]. |
| `tracker.enabled` | bool | Morning Gmail scan for application status. |

## Other database docs

| Doc / collection | Written by | Purpose |
|---|---|---|
| `engine/runbook` | setup / update | Copy of references/runbook.md (field `text`, plus `plugin_version`). |
| `engine/scan_py` | setup / update | Copy of scripts/scan.py (field `code`, plus `plugin_version`). |
| `engine/resume` | setup (optional) | Resume text when resume.source is "text". |
| `jobs/{id}` | runs + page | Scored jobs. |
| `outreach/{id}` | runs + page | Contacts tried and drafts made. |
| `outreach_requests/{id}` | page | "Draft email" button queue. |
| `apps/{thread_id}` | runs | Application tracker. |
| `runs/{run_id}` | runs | Live progress and drop log. |
| `seen/{YYYY-Www}` | runs | Keys already scanned. |
| `tasks/{id}` | page | The user's checklist. |
| `meta/status`, `meta/worker` | runs | Last run and worker heartbeat. |
