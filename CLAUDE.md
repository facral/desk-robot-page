# desk-robot-page

Participant session page for the desk-buddy robot study (ITMO master thesis, modular head-base
architecture). Participants talk to a pretend robot by calling its name; the browser turns speech
into text, the page computes face features with MediaPipe, and two CSV files go to a private Drive
folder through an Apps Script relay. No video or audio is recorded. The data feeds the robot's
intent estimator (when does a person address the robot).

This folder is kept separate from `../intent-wake` on purpose. It is merged there only when the
page is tested and stable (see docs/NEXT_STEPS.md, last section).

## Files
- `index.html`: the whole page. `CONFIG` at the top of the script, all text in the `TX` table.
- `apps-script/Code.gs`: upload relay, made from a Google Sheet (Extensions > Apps Script).
- `scripts/test_page.mjs`: self-check of text table, name calling and routing. Run after any change to `index.html`.
- `scripts/strip_speech.py`: removes speech text from an events file.
- `README.md`: setup, files, privacy, consent text. `docs/NEXT_STEPS.md`: ordered plan.

## Hard rules
- Events files contain participant speech in `heard` rows. Never open one or paste it into an LLM tool unless it went through `scripts/strip_speech.py` first. Quality checks run as local scripts.
- Never commit the `uploads` sheet, `.clasprc.json`, or anything from the Drive folder. The `/exec` endpoint URL may be committed.
- `index.html` and `Code.gs` are a matched pair: if you change an action name, a field, `CHUNK`, `ALLOWED_MIME` or `NAME_RE` in one, change the other and note it in `README.md`.
- Deliverable text in English. Every UI string has Indonesian, English and Russian with the same `{placeholders}`; `node scripts/test_page.mjs` checks this.
- Do not commit; leave changes for the owner to review.

## Known-good invariants (checked 2026-11-26)
- `CONFIG.CHUNK` = 3 MiB, equal to the relay's default `MAX_BYTES`, so every file goes in one chunk.
- Actions `init / chunk / status` and their fields match between page and relay.
- The page sends only `text/csv`, the relay accepts only `text/csv`, one chunk per file, at most 3 MiB (`MAX_BYTES` = `CONFIG.CHUNK`); the relay writes files with DriveApp, no Drive REST calls.
- File names `<code>_<laptop|phone>_events.csv` and `_features.csv` fit `NAME_RE`.
- No invite codes. The relay limits by file name, content, size (3 MiB) and `DAILY_MAX` files a day; page file names must keep matching its `NAME_RE`.
