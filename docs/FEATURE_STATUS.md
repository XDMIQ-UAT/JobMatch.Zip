# Public Feature Status (Agency-Managed)

Source of truth: GitHub Issues with label `feature` and one status label: `live`, `beta`, `coming`, or `planned`.

How it works
- Agencies create/update an issue using the “Feature status” form.
- Apply exactly one status label: `live` / `beta` / `coming` / `planned`.
- A GitHub Action regenerates `frontend/lib/features.ts` and the site updates automatically.

Where it shows up
- Pricing cards (landing pages)
- `/roadmap` page
- Future: README badges, emails

Notes
- No code edits required.
- Historical discussions stay in the issue thread.
- Changing status is as simple as relabeling the issue.