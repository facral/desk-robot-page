# Round two: is the version 4 data useful, the mumble loophole, and what would make the robot worth talking to

Date: 2026-11-17. Follows `ENGAGEMENT_ANALYSIS.md`. Based on the second real session (code YCU7DF, page version 4, the owner as participant).

What is measured and what is not:
- **Measured:** sessions 9S5UFP (version 2) and YCU7DF (version 4), one person, the owner.
- **Literature and web sources:** listed at the end.
- **Simulated:** eight future user groups walked through seven candidate activities by reasoning. Predictions, not observations.
- **Technical probe:** `tools/stt_probe.html`, run so far only in the app's embedded browser.

## 1. What session YCU7DF shows

| | Session 1 (v2) | Session 2 (v4) |
|---|---|---|
| Face visible | 91.8% | 99.8% |
| Sample rate, gaps | 10 Hz, none | 10 Hz, none |
| Addresses A / B / C | 17 / 4 / 8 | 11 / 6 / 9 |
| Robot busy in block A | 51% | 33% |
| Puzzles solved | not logged | 2, both after hints |
| Speech timing in the log | none | 53 segments in blocks |
| Space refused for silence | not possible | 4 times, all correct |
| Head pose, address vs silent work (0.5 = chance) | 0.54 to 0.66 | 0.68 overall; 0.70 to 0.82 per block |
| Enjoyment | 2 of 5 | 3 of 5 |

- Calibration worked: the look pose was held for 5 s (yaw -1.4, pitch -12.1). In the away phase the head swept from -41 to +40 degrees, so the logged median (yaw 2.3) is meaningless; use the samples, not the median.
- All four refusals were real: the next voice came 6 to 8 s later. The silence check does its job.
- Hints were used as intended: three for the first word puzzle, two for the number puzzle.
- Then the menu was toured: swap, time left, progress, riddle, coin, cheer, clock, fact, in that order. All ten goals were tried. This is the same "work through the list" behaviour as in session 1, moved from cards to chips.
- Voiced time in the 5 s before an accepted Space: median 2.0 s; 7 of 26 under 1.5 s and 3 under 1.0 s. Those are the candidate mumbles.

## 2. Is this recording useful?

**As a pilot and tool check: yes. As thesis data: not yet.**

Useful:
- The pipeline is clean and the log now carries real speech timing: 28 speech segments followed by Space and 25 that were not. Speech not addressed to the robot is exactly the hard negative an intent estimator needs.
- Separation by head pose improved, most in block C (yaw 0.82, pitch 0.78).

Not yet:
- While addressing the robot the head was 19 degrees away from the calibrated "look at the robot" pose (yaw 17 against -1.4), and about the same while the robot replied. The participant was not facing the robot when talking to it. Whether that is the menu, the keyboard or a changed sitting position cannot be told from the numbers. A model trained on this would learn "posture while using the menu", not "turning to the robot". This is blocker B4 again: the robot must sit apart from the work.
- One participant who knows the design. No conclusion about people in general.

## 3. Why it is still boring

1. **Speech carries no information.** The click on a chip already tells the page what is wanted. Speaking is a ceremony, so a mumble works as well as a sentence. This is the root of the loophole, not a detection problem.
2. **Every exchange is a dead end.** Ask, get one line, done. Nothing builds on the last exchange, nothing is at stake, the robot remembers nothing and never asks back.
3. **The "games" are trivia.** A fact, a riddle, a coin flip have no connection to what the person is doing at the desk.
4. **The robot shows no life between requests.** It only blinks. The ring during voice is the single contingent cue.

What research on desk robots says people value is different: a work companion's presence, clear work and break transitions and unobtrusive reminders [1]; a robot that works along in the person's rhythm, felt as a workmate [2]; goal reminders and emotional support during self-study, with goal reminders raising willingness to use the robot again [4]; a simple study companion that students with ADHD kept using voluntarily [3]. Expectations differ by person and context [5]. For talk itself, listening behaviour matters: backchannels and active listening raise the sense of being heard and how much people disclose [6]; responsive, not random, non-verbal backchannels raise trust [7]; a rule-based model on speech pauses was enough for children to prefer the attentive robot [8]; nodding and short verbal feedback raise perceived attentiveness and co-presence [9]; and backchannels directed at a quiet speaker increase that speaker's share of talk [10].

## 4. Closing the mumble loophole

| Option | What it does | Stops mumbling? | Privacy | Cost and risk |
|---|---|---|---|---|
| O1 Stricter loudness rule | Require at least 1.5 s of voiced sound | Short grunts only; "bla bla bla" passes | none | minutes of work; would have flagged 7 of 26 in session 2 |
| O2 On-device speech recognition in Chrome or Edge | Words are recognised locally; the spoken words choose the goal | Yes, speech becomes the control | audio stays on the device | Chrome and Edge 139+ only; language pack about 60 MB; Indonesian was named in a 2025 draft list but is unconfirmed; must be probed per machine |
| O3 Whisper in the browser (transformers.js) | Same, with a model the page downloads | Yes | audio stays on the device | 120 to 200 MB download, heavy on weak laptops next to the face tracker and recorder; needs a benchmark |
| O4 Transcribe afterwards, locally | A local script on the researcher's PC transcribes each recording and flags empty or nonsense utterances | Does not stop it, measures it | recording never leaves the PC; no LLM involved | one script; changes nothing for the participant |
| O5 Make the words matter to the speaker | Exchanges where the robot's reply does not depend on content but the person has a reason to say something real: state a goal, think aloud, practise speaking | Removes the incentive | none | redesign of content |

Recommendation: **O5 as the design answer, O4 as the quality check, O1 as a cheap guard, and O2 only if the probe says Indonesian is available locally.** Cloud recognition stays excluded.

Probe result so far: in the app's embedded browser (Chromium 156) the API exists, `processLocally` exists, and local recognition for `id-ID` and `en-US` reports `unavailable`. That browser is not a normal Chrome; the owner must run `tools/stt_probe.html` in their own Chrome and Edge. The probe never falls back to a server.

## 5. Simulated trials with future user groups

Activities: **M1** trivia one-liners (now), **M2** puzzle helper (now), **M3** focus companion (asks for a goal, keeps time, checks back), **M4** attentive listener (person thinks aloud, robot backchannels at pauses), **M5** voice utilities such as a timer (needs O2 or O3), **M6** speaking practice with feedback on speaking time and pauses, **M7** presence: eyes follow the face, small reactions.

Scale: `+` would use it, `0` indifferent, `-` annoyed or distracted.

| Group | M1 | M2 | M3 | M4 | M5 | M6 | M7 | Main reason |
|---|---|---|---|---|---|---|---|---|
| Students preparing for exams | 0 | 0 | + | + | + | 0 | + | explaining aloud helps learning; needs pacing |
| Programmers | - | 0 | + | + | + | 0 | 0 | rubber-duck habit; trivia breaks flow |
| Remote office workers | - | 0 | + | 0 | + | 0 | 0 | work and break rhythm, hands-free timer [1][2] |
| Writers and designers | 0 | 0 | 0 | + | 0 | 0 | + | talking an idea through; dislike being timed |
| People who struggle to focus | - | 0 | + | + | + | 0 | 0 | body doubling and goal reminders [3][4]; cues must be subtle |
| Language learners | 0 | 0 | 0 | + | 0 | + | + | need a reason and a listener to speak |
| Gamers and streamers | 0 | 0 | - | 0 | 0 | 0 | + | want reactions, not supervision |
| School children with homework | + | + | 0 | + | 0 | + | + | enjoy riddles; tell stories to an attentive robot [8] |

Reading: M3, M4 and M7 help most groups and annoy almost none. M1, the current filler, helps one group and annoys three. M5 is wanted but depends on local recognition. No single activity fits everyone, which matches the participatory-design finding [5].

## 6. Recommended version 5

1. **Trivia out, companion in.** Remove riddle, fact, coin and cheer from the default list. Keep hint, new puzzle, time left.
2. **Goal check-in and check-out (M3).** At the start of each block the robot asks what the person wants to get done; at the end it asks whether it worked. The reply adapts to how long the person spoke, measured locally.
3. **Listener mode (M4).** "Tell me what you are working on." While the person speaks, the robot gives small backchannels at pauses (a nod of the eyes, a soft sound), driven by the existing voice sensing. It closes with an open question.
4. **Speaking practice (M6)** as an option in the free block: 20 s on a prompt, then honest feedback on speaking time and number of pauses.
5. **Presence (M7).** The robot's eyes follow the face position from the tracker. The intro text must then say the robot knows where the face is, computed on the device.
6. **Loophole:** minimum 1.5 s of voice before Space counts (O1), local transcription script for quality control (O4), and voice-chosen goals if the probe passes (O2).
7. **Still open and more important than all of the above for the thesis:** put the robot apart from the work (blocker B4), for example on a phone beside the laptop.

Risks to state in the thesis: goal questions and listener prompts are robot-initiated, so they belong to the "prompted" class; eyes that follow the face attract gaze, which is realistic for the planned robot but changes the baseline.

## 7. Test series

Done:
- T1 session analysis, two sessions compared (section 1).
- T2 mumble rule replayed on session 2: a 1.5 s rule flags 7 of 26 accepted addresses.
- T3 local speech recognition probe built and run in the embedded browser: API present, Indonesian not available there.
- T4 simulated trials, eight groups by seven activities (section 5).

For the owner:
- T5 run `tools/stt_probe.html` in Chrome and in Edge; paste the result.
- T6 pilot with three to five real people from at least two of the groups above, half on version 4 and half on version 5.
- T7 one session with the robot page on a phone beside the laptop, to measure what B4 is worth.

## References

1. [Investigating Work Companion Robot Interactions to Enhance Work-from-Home Productivity and Experience](https://consensus.app/papers/details/w:ebb67749-81dd-4a7e-9a5c-3fc4d0d60ed6/?utm_source=claude_desktop) (Kim et al., 2024, Archives of Design Research, 2 citations)
2. [Evaluating How Desktop Companion Robot Behaviors Influence Work Experience and Robot Perception](https://consensus.app/papers/details/w:2d003395-004c-4673-a23e-fbea605e26c3/?utm_source=claude_desktop) (Yoon et al., 2024, CHI Extended Abstracts, 5 citations)
3. [Design and Evaluation of a Socially Assistive Robot Schoolwork Companion for College Students with ADHD](https://consensus.app/papers/details/w:c94a632b-344b-4cae-834d-2de221a7fedd/?utm_source=claude_desktop) (O'Connell et al., 2024, ACM/IEEE HRI, 39 citations)
4. [Motivating Students' Self-study with Goal Reminder and Emotional Support](https://consensus.app/papers/details/w:a2b37f7a-3296-4e61-bac0-1384e1e32051/?utm_source=claude_desktop) (Cho et al., 2025, IEEE RO-MAN, 0 citations)
5. [Envisioning an Attention-Supportive Desktop Robot: A Participatory Design Study](https://consensus.app/papers/details/w:5142ade5-1d81-46ac-b3ba-90d4e24e02d7/?utm_source=claude_desktop) (Xiang et al., 2026, ACM/IEEE HRI, 0 citations)
6. [A Robot That Listens: Enhancing Self-Disclosure and Engagement Through Sentiment-based Backchannels and Active Listening](https://consensus.app/papers/details/w:6b3c72f3-9b5e-4e6b-8933-bfaeb1bb0a05/?utm_source=claude_desktop) (Tran et al., 2025, IEEE RO-MAN, 8 citations)
7. [Embodied Active Listening: How Non-Verbal Backchannel Behaviour Influences Trust and Perception of a Social Robot](https://consensus.app/papers/details/w:c86d595b-ce5a-4c17-947a-9cbe2119dae5/?utm_source=claude_desktop) (Reyes-Cruz et al., 2026, ACM CUI, 1 citation)
8. [Telling Stories to Robots](https://consensus.app/papers/details/w:b8195e9d-3c06-4d53-b98f-b6180020c213/?utm_source=claude_desktop) (Park et al., 2017, ACM/IEEE HRI, 123 citations)
9. [Does Listening Matter? Backchanneling and Nodding in AI Clone](https://consensus.app/papers/details/w:a9ade92a-8a88-423c-a074-1825e3e17a1e/?utm_source=claude_desktop) (Inoue et al., 2026, ICMI Companion, 0 citations)
10. [Socio-cultural perception of robot backchannels](https://consensus.app/papers/details/w:37089da5-b0f0-42dc-b623-5f560ae347dd/?utm_source=claude_desktop) (Engwall et al., 2023, Frontiers in Robotics and AI, 15 citations)

Web sources on local speech recognition:
- [SpeechRecognition: processLocally property (MDN)](https://developer.mozilla.org/docs/Web/API/SpeechRecognition/processLocally)
- [SpeechRecognition: available() static method (MDN)](https://developer.mozilla.org/docs/Web/API/SpeechRecognition/available_static)
- [SpeechRecognition: install() static method (MDN)](https://developer.mozilla.org/docs/Web/API/SpeechRecognition/install_static)
- [Intent to Ship: On-device Web Speech API (blink-dev)](https://groups.google.com/a/chromium.org/g/blink-dev/c/VNOok2dbmHM)
- [On-device speech recognition with the Web Speech API (Chrome AI dev preview)](https://groups.google.com/a/chromium.org/g/chrome-ai-dev-preview-discuss/c/Rlyc2uAsFCY)
- [Expanding on-device AI in Microsoft Edge (Edge blog, June 2026)](https://blogs.windows.com/msedgedev/2026/06/02/expanding-on-device-ai-in-microsoft-edge-new-models-and-apis-for-the-web/)
- [Browser Speech Recognition in 2026: Whisper and the STT Landscape](https://offlinetts.com/blog/browser-speech-recognition-whisper-comparison/)
- [whisper-web (transformers.js demo)](https://github.com/xenova/whisper-web)
