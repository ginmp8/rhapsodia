# Edit-items workflow

1. Resolve exactly one existing workspace and read complete `outline.yaml` and relevant results.
2. Apply requested additions/removals/clarifications while preserving topic, research scope, output language and execution settings. Discover new candidates from current sources only when asked.
3. Deduplicate by canonical identity and aliases; similar names do not justify merging distinct objects. Maintain stable `items[].id` across renames; generate unique filename-safe IDs for new items where useful.
4. Retain original order and append new items unless requested otherwise. Do not delete old result JSON when removing an item; preserve user data and report the orphan for review.
5. Modify only the `items` collection unless explicitly authorized. Validate `outline.yaml`; changing item membership or name changes the scope fingerprint, so existing stamped results need a targeted resume review rather than automatic reuse.
6. Report IDs/names added/removed/edited, any incompatible changes and validation results.
