# Desk-robot session page v7

A single static page (`index.html`) that guides a participant through an 11-minute session with a pretend desk robot. The participant talks to the robot by calling its name; the browser turns speech into text and the robot answers by keyword. The page computes face features on the device and sends two CSV files to a private Google Drive folder through a small Apps Script relay (`apps-script/Code.gs`). **No video, audio or photos are recorded or sent.**

## Session

1. **Setup.** A 3/4-view drawing shows where to put the device (laptop raised to eye height vs lying flat; phone on a stand vs flat on the table), with the camera's view cone, drawn as inline SVG in the page colours (`guideSvg` in `index.html`; a copy is on the Superdesign canvas "Desk Robot Setup Illustrations"). A dashed outline on the camera preview turns green when the face is at a good size. The participant says the robot's name once to test the microphone. The page says whether speech is recognised on the device or by the browser maker's service.
2. **Calibration.** Look at the robot, then turn away. The countdown only runs while the pose is right.
3. **Warm-up.** Say hello, ask the time, from example sentences on screen. Not counted.
4. **Parts 1 and 2, mini detective.** Six short cases in a fixed order (cake, charger, window, coffee machine, lab key, lunch). Only the robot knows the clues; the participant asks about each suspect and the topics shown, then picks the culprit. A solved case is replaced by the next one after four seconds, and part 2 continues where part 1 stopped. "Next case" skips one. Part 2 has three breaks.
6. **Part 3, free time.** Listener mode ("listen to me", the robot nods at pauses, "done" ends it) and 20-second speaking practice.
7. **End.** The participant reads every transcribed sentence, can delete any or all of them, rates the session, answers three optional trait questions, then sends or deletes everything.

**Talking to the robot.** The robot answers only when its name is in the sentence ("Budi, where was Bima?"). Every part shows three example sentences, and the part's intro repeats them. A sentence counts as finished after `END_PAUSE_MS` (1.3 s) without new words, so a short pause mid-sentence does not trigger an answer; pieces are joined. Speech without the name is logged but not answered. Every recogniser guess is tried, and the screen shows what was heard ("I heard: ..."). When nothing matches, the robot repeats what it heard and gives an example.

**Correcting the robot.** For `CORRECT_MS` (8 s) after an answer, saying "wrong, it should be ..." (no name needed) is logged as a correction, and "I was not talking to you" as such. Saying nothing means no complaint. The robot also asks for a goal at the start of each part and checks back near the end, and offers to listen in free time if nobody talked to it; these are logged as robot-initiated and never start while the participant is talking.

**Position warnings.** When the face is lost, too far, too close or at the edge of the frame for `POS_WARN_MS` (3 s), the robot says so, at most once per `POS_COOLDOWN_MS` (20 s), and not during breaks. Turning the head away does not count.

**Phone and laptop.** The page tells them apart (touch screen narrower than 600 px means phone; `?device=phone|laptop` overrides). The device is in the file names, the file headers and the `config` event, and the face-size thresholds differ. The screen is kept awake on phones during the session.

**Languages.** Indonesian, English, Russian, chosen by `?lang=id|en|ru`, otherwise Russian for a Russian browser and Indonesian for everything else. All text sits in one table, `TX`, one row per string with the three languages side by side.

## Files sent

| File | Contents |
|---|---|
| `<code>_<device>_events.csv` | Session timeline. `heard` rows hold the speech text as `target|text` (target is `robot`, `answer`, `listen` or `none`). Also `intent` (`fact:<id>`, `clue`, `swap`, `time`, `left`, `score`, `hello`, `listen`, `practice`, `free`), `reply_*`, `feedback` (`k=<intent>;v=corrected|notme|none|next`, the correction words are in the `heard` row just before), `case_start`, `case_end` (`<case>;solved|skip`), `case_accuse` (`<case>;<suspect>;right=0|1`), `pos_warn` (`none|far|near|edge`), `pos_ok`, `robot_ask`, `reply_prompted`, `rating`, `traits`, `config`. |
| `<code>_<device>_features.csv` | 10 Hz: `face`, yaw, pitch, roll (degrees, sign unverified), face box width, centre x and y, `eye_h`, `eye_v` (gaze from blendshapes, -1 to 1, sign unverified) and `jaw_open` (0 to 1). Rows with `face=0` are missing data. |

Times are milliseconds from `session_start`. Speech times come from the recogniser and lag the voice by a few hundred milliseconds.

**Before giving an events file to anyone, or to any AI tool, remove the speech text:** `python scripts/strip_speech.py CODE_laptop_events.csv` writes `CODE_laptop_events_nospeech.csv`.

## Setup (about 15 minutes)

1. **Drive folder.** A private folder, shared only with the researchers. Copy its id from the URL.
2. **Sheet and script.** Create a Google Sheet, open **Extensions > Apps Script**, paste `apps-script/Code.gs`. It must be made from the sheet: the relay refuses uploads when it has no sheet, because the `uploads` sheet is the only record of which invite code sent which session.
3. **Script properties** (Project Settings): `FOLDER_ID`, `INVITES` (comma-separated codes of 8 or more random characters). Optional: `MAX_BYTES` (default 3 MiB, one chunk per file), `MAX_USES` (default 12, two files per session).
4. **Deploy** as a web app: Execute as = Me, Who has access = Anyone. Copy the `/exec` URL.
5. **Page.** Set `CONFIG.ENDPOINT` in `index.html` to that URL, and `CONSENT_URL`, `RESEARCHER`, `CONTACT`. The endpoint may be public; the invite codes and the sheet may not.
6. **Host** on GitHub Pages (camera and microphone need https).
7. **Try it** with an invite code; the Drive folder should show the two CSV files.

With `ENDPOINT` empty the page runs in demo mode: nothing is sent and the files are offered for download. `#fast` in the URL shortens every part to 40 seconds.

## Checks

- `node scripts/test_page.mjs`: every string exists in all three languages with the same `{placeholders}`; name calling and keyword routing give the expected result.
- `python scripts/test_upload.py --negative` and `--size-mb 1` against the real relay (or `scripts/mock_relay.py` offline).
- `tools/stt_probe.html`: whether this browser can recognise Indonesian, English or Russian on the device.

## What was tested and what was not

Version 7 tested on 2026-11-26 with a fake camera, a mock face tracker and a mock speech recogniser: a sentence split by a pause is answered once, as a whole; a spoken correction and a "not talking to you" are logged; examples follow the current case; a solved case is replaced by the next and part 2 continues it; "next case" skips; an unrecognised question gets the heard text and an example; the face warning appears after 3 s and is not repeated within the cooldown; the edge warning shows in setup. Version 6 tests (setup, calibration, listener mode, practice, review and delete, recovery, phone width, Russian) still apply. `node scripts/test_page.mjs` checks every case in every language.

Not tested: a real microphone and recogniser in each language (keyword routing depends on what the recogniser writes; the 1.3 s end pause may need tuning), real cameras on phones, the eye and mouth columns with a real face, Safari and iPhone, and the real Apps Script relay.

## Privacy notes

- The page itself stores and sends no video, audio or photos. Camera frames are reduced to numbers on the device.
- The microphone opens only while the consent box is ticked, and closes when the session ends. Once data has been sent or deleted, nothing is written back to the browser, and delete buttons disappear as soon as any file has left the device.
- Speech recognition is done by the browser. Where the browser offers on-device recognition for the language, it is used; otherwise the browser sends the audio to its maker (Google for Chrome, Apple for Safari). The setup screen tells the participant which.
- Speech text is personal data. The participant reviews and can delete it before sending. Until sent or deleted, the session is kept in this browser's local storage so a closed tab does not lose it.
- Files carry a random session code. The link to a person is the invite code in the `uploads` sheet; keep that sheet restricted and separate from the folder.

## Suggested consent wording (adapt, and have it checked with ITMO)

> During the session (about 11 minutes) the page uses your camera and microphone. No video, audio or photos are stored. The page sends to the researchers: numbers describing your head, eye and mouth movement, the text of what you said during the session, the timing of the session, your ratings, and your device type. To turn your speech into text, your browser may send your voice to its maker (for example Google); the setup screen tells you whether this happens. You can read and delete the text before sending, and you can stop at any time. Files are named with a random code, not your name. You may ask us to delete your data by giving us your session code. Data will be deleted on [date]. Researchers: [names, contact].

Open questions to settle outside this repo: ITMO ethics approval, whether sending speech to Google's recogniser is acceptable for your participants, and the deletion date.
