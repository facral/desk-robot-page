# desk-robot-page

Participant session page for the desk-buddy robot study (ITMO master thesis, modular head-base
architecture). The page records a 12-minute webcam session, extracts head pose with MediaPipe in
the browser, and uploads video + CSVs to a private Drive folder through an Apps Script relay.
The data feeds the robot's intent estimator (when does a person want to engage the robot).

This folder is kept separate from `../intent-wake` on purpose. It is merged there only when the
page is tested and stable (see docs/NEXT_STEPS.md, last section).

## Files
- `index.html`: the whole page (UI text in Indonesian, config block `CONFIG` near line 337).
- `apps-script/Code.gs`: upload relay, deployed manually at script.google.com (or via clasp).
- `README.md`: original setup notes and the list of untested items.
- `docs/NEXT_STEPS.md`: ordered plan, tagged human vs Claude.

## Hard rules
- Raw participant video or audio must never be opened, summarised, or sent to any LLM tool. Quality checks run as local scripts only.
- Never commit invite codes, the Apps Script endpoint URL with live data, `.clasprc.json`, or anything from the Drive folder.
- `index.html` and `Code.gs` are a matched pair: if you change an action name, a field, `CHUNK`, `ALLOWED_MIME` or `NAME_RE` in one, change the other and note it in `README.md`.
- Deliverable text in English; the participant-facing UI stays Indonesian (and the existing EN toggle).
- Do not commit; leave changes for the owner to review.

## Known-good invariants (checked 2026-11-16)
- `CONFIG.CHUNK` = 3 MiB = 12 x 262144, as Drive resumable upload requires.
- Actions `init / chunk / status` and their fields match between page and relay.
- The page strips `;codecs=...` before sending `mime`, so `ALLOWED_MIME` matches.
- File names `<code>_video.webm|.mp4`, `<code>_features.csv`, `<code>_events.csv` fit `NAME_RE`.
- `MAX_USES` 12 = 3 files x 4 attempts per invite.
