# Interactivity analysis: why the session feels flat, and what to change

Date: 2026-11-17. Scope: the content of the session page (cards, puzzles, robot replies), not its bugs. Bugs are in `BETA_TEST_REPORT.md`.

## What this is and is not

- **Measured:** one real session (code 9S5UFP, the owner as participant).
- **From literature:** twelve papers on social presence, personality and addressee detection, listed at the end.
- **Simulated:** six participant personas walked through the content by reasoning. These are predictions to check in a pilot, not observations of people.

## 1. What the real session shows

| Block | Robot addressed | One exchange every | Card shown to Space (median) | Robot busy |
|---|---|---|---|---|
| A, word puzzles | 17 times | 10.6 s | 4.1 s | 51% of the block |
| B, numbers + breaks | 4 times | 45 s | 33 s | 12% |
| C, free time | 8 times | 22.5 s | 8.0 s | 26% |

- In block A the participant worked through the cards like a list. The puzzle was barely touched (one skip logged).
- One Space press came 0.8 s after the card appeared. Nobody can say a sentence in that time, so Space does not prove speech.
- Self-ratings: arousal 1 of 5 in block A, "a greeting now would bother me" in A and B, enjoyment 2 of 5.

Reading: block A produced many "talks to robot" labels, but they are a compliance loop, not moments of wanting the robot.

## 2. Psychological diagnosis

1. **No reason to talk.** Self-determination theory names three needs. Autonomy is low (the card dictates the sentence), competence is untouched (talking gains nothing), relatedness is absent (the robot knows nothing about the person). Version 3 started to fix competence with hint and swap cards.
2. **The robot is not contingent.** It answers after a fixed delay whatever was said, and the page states that it cannot hear. Contingent, context-aware responses are what raise social presence and engagement [1][2][3][4]; response behaviour, not only appearance, drives perceived presence [12].
3. **Reading aloud is not addressing.** A person reading a sentence looks at the card. Mutual gaze at the end of an utterance is a main cue for "this was said to the robot" [9], and gaze features are what lift intention-to-interact prediction [10]. Scripted cards therefore suppress the signal the study wants. This fits the weak head-pose separation found in session 9S5UFP.
4. **Demand characteristics.** Conscientious people treat cards as tasks to finish. Their behaviour says "I comply", not "I intend".
5. **Habituation.** Many near-identical exchanges with the same timing become predictable within a minute.
6. **Evaluation apprehension.** Speaking aloud to a screen while being recorded is awkward, more so with other people in the room.
7. **People differ.** Extraverts talk more and longer to a robot; people with negative attitudes look at its face less [5]. Extraversion also predicted how often people started routines with a voice assistant [8]. A general propensity to interact may matter more than specific traits [7], and the evidence overall is mixed [6]. So low talkers are expected, not a defect.

## 3. Six simulated personas

| Persona | Trait behind it | Predicted behaviour on the current page | Where it breaks |
|---|---|---|---|
| Enthusiast | high extraversion, openness | Talks a lot, improvises, asks own questions | Free questions get one of three stock replies; feels fooled, engagement drops in block C |
| Quiet one | introversion, self-consciousness | Speaks rarely and softly, may press Space without speaking | Emotional cards ("cheer me up", "greet me in your home language") are skipped; labels become wrong |
| Rule follower | high conscientiousness | Does every card in order, reads verbatim | Produces the block A pattern above: many labels, little intent, eyes on the card |
| Skeptic | low agreeableness, negative attitude to robots | Solves puzzles or uses the phone, ignores the robot | Zero addresses; only the nudge appears; leaves the frame in block C |
| Achiever | task focus, need for achievement | Wants to solve puzzles; robot is a distraction | "No score" removes the goal; uses the robot only if it helps |
| Privacy-minded | high concern about recording | Stiff, self-monitoring, short utterances | May stop the session; today that still pushes "send recording" |

Improvisation test: only the Enthusiast improvises, and the page handles it worst. Every other persona stays inside the script, and the script is what flattens the data.

## 4. Candidate solutions scored against the personas

Scale: `+` helps, `0` neutral, `-` harms.

| Solution | Enthusiast | Quiet | Rule follower | Skeptic | Achiever | Privacy | Label quality | Privacy cost | Same robot for all |
|---|---|---|---|---|---|---|---|---|---|
| S1 Scripted cards (now) | 0 | - | - | - | - | 0 | - | none | yes |
| S2 Robot is needed for the task, goals instead of sentences | + | + | + | 0 | + | 0 | + | none | yes |
| S3 Robot senses voice locally (level only) | + | + | 0 | 0 | 0 | 0 | + | none, if said clearly | yes |
| S4 Cloud speech recognition + keyword search | + | 0 | 0 | 0 | 0 | - | 0 | audio leaves the device | browser dependent |
| S5 Free chat with a language model | + | 0 | 0 | 0 | - | - | - | text leaves the device | no |
| S6 Two gentle robot-initiated moments per block, tagged | 0 | + | 0 | + | 0 | 0 | + if tagged | none | yes |
| S7 Warm-up round and "you are alone with it" framing | 0 | + | 0 | 0 | 0 | + | + | none | yes |
| S8 Three trait questions after the session | 0 | 0 | 0 | 0 | 0 | 0 | + for analysis | minimal | yes |

## 5. Recommended design: a robot that is needed, not a robot one is told to talk to

**S2 + S3 as the core, S6 as a floor for quiet people, S7 and S8 as cheap support.**

1. **Make the robot hold something the participant wants.** Harder puzzles, and the robot is the only source of hints, puzzle swaps, an answer check and the remaining time. The participant decides when to ask. Need varies with puzzle difficulty, so intent varies naturally within one person.
2. **Replace sentences with goals.** A card shows "ask for a hint", not the words. People phrase it themselves and look up while speaking. The card still tells the page which reply to give, so no speech recognition is needed.
3. **Let the robot visibly listen.** Measure microphone level in the browser. The ring lights up while there is voice; if Space arrives with no voice the robot says "I did not hear you". Log `speech_start` and `speech_end`. This gives contingency and honest labels without sending audio anywhere. The intro text must then say: the robot notices that you speak, not what you say.
4. **A floor, not a quota.** If a block passes 60% with no address, the robot makes one short offer ("want a strange fact? say yes"). Tag these `prompted`; analyse them apart from spontaneous addresses. Proactive speech is a different class, and most people prefer to start the interaction themselves [7].
5. **Warm-up.** Two practice exchanges before the first block, recorded but tagged `warmup`, so the first awkward attempts do not count.
6. **Measure the person.** After the session: two extraversion items, one "comfort talking to voice assistants" item. Then engagement can be explained instead of treated as noise.

**Low-engagement participants are valid data.** They are the people a real desk robot must not disturb. Do not push them with scores or quotas; guarantee the two tagged prompted moments per block and keep the rest.

**Not recommended now:** cloud speech recognition (S4) and free chat (S5). Both send participant speech off the device, need a new consent text and ethics check, behave differently per browser, and give each participant a different robot. Revisit S4 only if a pilot shows the recommended design still feels flat.

## 6. How to check this with real people

Pilot with four to six people, half on the current page and half on the redesign. Compare:
- addresses per block, split spontaneous vs prompted;
- time from card to Space, and share of Space presses without voice;
- puzzles solved (is the filler task alive?);
- separation of head pose between address and non-address moments;
- enjoyment rating and the three trait items.

The redesign wins if spontaneous addresses are fewer but better separated, the filler task is used, and enjoyment rises.

## References

1. [How Conversational Contingency Shapes Trust in Human-AI Interaction: Evidence from a Two-Wave Mediation Study](https://consensus.app/papers/details/w:6a4ed93a-4a38-4d05-989d-368174bbb7e2/?utm_source=claude_desktop) (Cao et al., 2025, Journal of Broadcasting & Electronic Media, 9 citations)
2. [Responsive Joint Attention in Human-Robot Interaction](https://consensus.app/papers/details/w:9fdf0e90-90b1-4153-aba2-d1e246ddfa30/?utm_source=claude_desktop) (Pereira et al., 2019, IROS, 31 citations)
3. [Implementation of a Biologically Inspired Responsive Joint Attention System for a Social Robot](https://consensus.app/papers/details/w:b7fbfe8c-7e66-4931-af99-061f21f10495/?utm_source=claude_desktop) (García et al., 2025, Advanced Intelligent Systems, 4 citations)
4. [Copresence With Virtual Humans in Mixed Reality: The Impact of Contextual Responsiveness on Social Perceptions](https://consensus.app/papers/details/w:74c32982-df23-4c2c-9fac-a7122a823a84/?utm_source=claude_desktop) (Pimentel et al., 2021, Frontiers in Robotics and AI, 48 citations)
5. [Towards Engagement Models that Consider Individual Factors in HRI: On the Relation of Extroversion and Negative Attitude Towards Robots to Gaze and Speech During a Human–Robot Assembly Task](https://consensus.app/papers/details/w:4e0550b7-6726-4639-8f22-dec46ab3bdf3/?utm_source=claude_desktop) (Ivaldi et al., 2016, International Journal of Social Robotics, 120 citations)
6. [Influence of User Personality Traits and Attitudes on Interactions With Social Robots: Systematic Review](https://consensus.app/papers/details/w:bc082ee5-988a-49dd-a7e1-a9160c77604c/?utm_source=claude_desktop) (Kabacińska et al., 2025, Collabra Psychology, 28 citations)
7. [Desirability of Proactive Robots: A User Study on Spoken Interaction Initiation](https://consensus.app/papers/details/w:e7c18495-8a25-4bdd-88a0-c8248660446c/?utm_source=claude_desktop) (Viswanath et al., 2026, ACM/IEEE HRI, 3 citations)
8. [Evaluating Older Adults' Engagement and Usability With AI-Driven Interventions: Randomized Pilot Study](https://consensus.app/papers/details/w:fc4dda09-00da-4ac4-af76-a22df3b5e960/?utm_source=claude_desktop) (Shade et al., 2024, JMIR Formative Research, 22 citations)
9. [Are you talking to me?](https://consensus.app/papers/details/w:4dbf90db-6fd8-45c8-9433-b5adaee81886/?utm_source=claude_desktop) (Richter et al., 2016, International Conference on Human-Agent Interaction, 36 citations)
10. [Predicting the Intention to Interact with a Service Robot: the Role of Gaze Cues](https://consensus.app/papers/details/w:5689c4e8-308b-4669-8f37-b8e5e8c17df5/?utm_source=claude_desktop) (Arreghini et al., 2024, IEEE ICRA, 17 citations)
11. [Starting engagement detection towards a companion robot using multimodal features](https://consensus.app/papers/details/w:4e3546fd-c7de-4995-b733-4946f428b96d/?utm_source=claude_desktop) (Vaufreydaz et al., 2015, Robotics and Autonomous Systems, 73 citations)
12. [Users' responses to humanoid social robots: A social response view](https://consensus.app/papers/details/w:56ffc569-6299-4541-a4dd-e2a2a3cd3e62/?utm_source=claude_desktop) (Premathilake et al., 2024, Telematics and Informatics, 38 citations)
