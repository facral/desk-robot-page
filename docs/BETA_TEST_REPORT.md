# Beta test report: session page v3

Date: 2026-11-17. Build: local working copy, page version 3 (not yet published).

## How it was tested

One tester (Claude) walked the whole participant flow in a desktop browser at 1024x768 and at phone size 375x812, in Indonesian and English. The camera was a fake stream and the face tracker was a mock, except for one run with the real permission prompt, which the browser refused. Edge cases tried: camera refused, Start pressed too early, Space while typing, Enter in the answer box, language switch mid-session, abort, reload and recovery, end screen in demo mode. The code was read for things that cannot be triggered in a browser pane (sleep, hidden tab, upload errors).

Evidence labels: **seen** = reproduced in the browser; **code** = read in `index.html`, not reproduced; **data** = from the real session 9S5UFP.

## Blockers: can lose a session or make the data unusable

| # | Finding | Evidence | Suggested fix |
|---|---|---|---|
| B1 | Space does nothing while the cursor is in the answer box. After typing an answer the cursor stays there, so "speak, then press Space" fails silently and types a space instead. | seen | Let Space call the robot from the answer box too (answers never contain spaces), or move focus out after Check. |
| B2 | The invite code is only checked when uploading, after the whole session. A typo costs the participant 10 minutes and ends in a generic failure. | code | Check the code before Start with a small `check` action in the relay. Show the relay's reason (`invite`, `uses`, `size`) on failure. |
| B3 | Nothing keeps the laptop awake and nothing reacts when the tab is hidden. In block C ("do anything") the screen can dim or sleep and tracking stops; a hidden tab is logged but the participant is not told. | code | Request a screen wake lock during the session. When the tab is hidden, pause the block timer and show "come back to this tab". |
| B4 | Robot, card and puzzle sit within about 250 px of each other. Looking from the puzzle to the robot is an eye movement of a few degrees, so the head barely turns. This matches the session data, where head pose hardly separated talking to the robot from other moments. | seen + data | Decide on the layout: robot far to one side of a wide window, or the robot on a second device beside the laptop. Also consider eye-direction columns in the features file. |
| B5 | "End session" leads to the same "Done, thank you" screen and still asks to send the recording. There is no way to discard it. | seen | After an abort, ask "send what was recorded" or "delete it", and make delete clear the local backup. |

## Major: confusing or risky, session still completes

| # | Finding | Evidence | Suggested fix |
|---|---|---|---|
| M1 | Every camera error shows "permission denied". A camera used by another app, no camera, or an in-app browser (links opened from Telegram or WhatsApp) get the wrong advice. | seen for refusal, code for the rest | Separate messages per error name; detect in-app browsers and say "open in Chrome". |
| M2 | Start stays disabled with no reason. The checklist asks "my face is fully visible in the preview" before the camera is switched on. | seen | Put the camera check first; under Start, list what is still missing. |
| M3 | The robot's voice depends on voices installed on the device. In the test browser there was no Indonesian voice, so the robot was text only. Participants get different robots, and reading captions pulls gaze to the robot. | seen | Decide one condition for everyone: always text, or bundled audio clips. Log `voice=on/off` per session. |
| M4 | Recovery after a closed tab restores the video only; events and features are gone, so the video has no timeline. The banner stays in demo mode, and the next person on the same browser can download the previous person's video. | seen | Back up events and features with the video chunks. Tie recovery to the session code and offer "delete" next to "send". |
| M5 | No microphone check. A muted or wrong microphone is only discovered during analysis. | code | Add a level meter to the camera check and require some sound before Start. |
| M6 | Space is trusted as "I just spoke to the robot". Nothing checks that the person spoke, so labels can be wrong. | design | Measure microphone level locally (no audio leaves the device), log `speech_start` and `speech_end`, and let the robot say "I did not catch that" when Space comes with silence. |
| M7 | On a phone the answer box is below the fold, the robot scrolls off screen while typing, and the instruction says "press Space". The page does not warn phone users. | seen | Detect small or touch screens on the first page and ask for a laptop, or design a phone layout on purpose. |

## Minor

- Old text from the phone-camera version: "stay inside the phone frame" on the calibration screen, "write this code in your video file name" in setup. (seen)
- Setup says "until it says Sent", which never appears in demo mode. The intro points to a consent form, but no link is shown while `CONSENT_URL` is empty. (seen)
- Language can be switched mid-session: the interface changes, the current puzzle stays in the old language, and the log records one language. Lock it at Start. (seen)
- Enjoyment is logged on every click (5 then 3 gives two rows). Log once at send time, or document "last click wins". (seen)
- Stated duration differs: page 11 minutes, README 12, real session 10. (data)
- No recording indicator on screen during the session. (seen)
- The end screen shows a raw CSV box and, in the fallback, three separate save buttons. One "save everything" button is easier. (seen)
- A break banner can overlap a robot reply, and `break_end` can land after `block_end`. (data)
- Block C lets people leave the camera view: 42 seconds without a face in session 9S5UFP. Say "stay in front of the camera" in the block text. (data)

## What works well

Pose-gated calibration, self-view hidden during blocks, Enter submits an answer, the abort dialog defaults to "continue", no sideways scrolling on a phone, leaving the page during recording asks for confirmation, demo mode saves files locally.

## Limits of this test

- No real camera, no real face, no real microphone: thresholds, lighting and tracking speed are untested.
- One browser engine on one machine. Safari, Firefox, Android and iPhone are untested.
- The real upload relay was not used.
- The tester knows the code. First-time confusion is under-reported.

## A better test round

1. Fix B1, B2, B3, B5 first; they are cheap and each can waste a participant.
2. Decide B4 before collecting data, because it changes what the data can answer.
3. Run three to five people who have never seen the page. Give them only the link, sit beside them, and ask them to think aloud. Write down every place they hesitate.
4. Cover a small device matrix: Chrome and Edge on Windows, Safari on a Mac, one slow laptop, one external webcam.
5. Run one full session against the real relay per browser and check the three files in Drive.
6. After each session run `scripts/check_signs.py` once, then a quality check on the CSVs before trusting the recording.
