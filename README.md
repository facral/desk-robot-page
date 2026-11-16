# Desk-robot session page v2

A single static page (`index.html`) that guides a participant through a 12-minute session, records the webcam in the browser, and sends the files to a private Google Drive folder through a small Apps Script relay (`apps-script/Code.gs`).

## What was tested and what was not

Tested here with a fake camera and a mock upload server: the full flow, 3 upload files, a forced failure with retry, features-only mode, abort path, demo mode.

Not tested, and must be tested by you before recruiting:
- The real Apps Script and Drive (init, chunk, status), especially a 100+ MB upload.
- The MediaPipe face check and head-pose numbers with a real camera and the real model download.
- Safari and iPhone, Firefox, and Android Chrome.
- The sign convention of yaw and pitch (turn your head left and right, up and down, and compare the features CSV).

## Setup (about 15 minutes)

1. **Drive folder.** Create a private folder in Google Drive. Share it only with you and your teammate. Copy its id from the URL.
2. **Apps Script.** Go to script.google.com, create a project, paste `apps-script/Code.gs`.
3. **Script properties** (Project Settings): `FOLDER_ID` = the folder id; `INVITES` = comma-separated codes you will hand out, for example `AB12CD,EF34GH`. Optional: `MAX_BYTES`, `MAX_USES`.
4. **Deploy** as a web app: Execute as = Me, Who has access = Anyone. Approve the Drive permission when asked. Copy the web app URL (ends with `/exec`).
5. **Page.** In `index.html` set `CONFIG.ENDPOINT` to that URL. Optionally set `CONSENT_URL`, `RESEARCHER`, `CONTACT`.
6. **Host** the page on GitHub Pages (any static https host works). Camera access needs https.
7. **Try it yourself** with an invite code, then open the Drive folder: you should see `<code>_events.csv`, `<code>_features.csv`, `<code>_video.webm`.

If `ENDPOINT` is empty the page runs in demo mode: nothing is sent and the files are offered for download. Use it for your own tests.

## Modes

- `video` (default): records video and audio, uploads video plus the head-pose CSV and the event log.
- `features`: no video and no audio are recorded; only head-pose numbers and the event log are uploaded. Use it if storing face video is not allowed. Open the page with `?mode=features`, or set `CONFIG.MODE`.
  Limitation: audio features for the exploratory voice study are not available in this mode.

Test mode: add `#fast` to the URL (12-second blocks).

## What the files contain

- `_video.webm` (or `.mp4` on Safari): the recording. Browser recordings carry no duration metadata; remux before analysis, for example `ffmpeg -i in.webm -c copy out.webm`.
- `_features.csv`: at 10 Hz, `face` flag, yaw, pitch, roll (degrees, order YXZ, sign convention unverified), face box width, center x and y. Rows with `face=0` are missing data, not negatives.
- `_events.csv`: session timeline (blocks, cards, breaks, ratings). Times are in milliseconds from `session_start`, which is the same moment the recorder starts, so video and events align without a sync beep.

## Privacy notes

- The file name contains only a random session code. The link between a person and a recording is the invite code, kept in the Apps Script sheet `uploads` (if you create it). Keep that sheet separate from the videos and restricted.
- The invite code check, the size and type limits, and the per-code upload limit in `Code.gs` are what stop strangers from filling your Drive. The endpoint URL is visible in the page source.
- If the tab closes before sending, the recording is kept in the browser (IndexedDB) and the page offers to send it on the next visit from the same browser.
- Raw video must not be given to any LLM agent. Run quality checks locally.

## Suggested consent wording (adapt, and have it checked with ITMO)

> The page records video and audio of you from your laptop camera and microphone during the session (about 12 minutes). The recording and a log of the session are stored in a Google Drive folder with restricted access, readable only by the researchers named below. Files are named with a random code, not your name. The data is used only for this course research project. You may stop at any time. You may ask us to delete your recording by giving us your invite code. Data will be deleted on [date]. Researchers: [names, contact].

Open questions you must settle outside this repo: whether ITMO requires ethics approval, whether storing face video on Google Drive is allowed for your participants (data-localization rules may apply), and the deletion date.
