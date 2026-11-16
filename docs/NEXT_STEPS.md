# Next steps for the session page

Tags: **[you]** needs your account, device, or a decision. **[claude]** can be done by Claude Code here, unattended or on request.

Status 2026-11-16: files copied from Downloads into this folder, git initialised, nothing committed.
Smoke test: the page opens in demo mode with no console errors. Cross-check of `index.html` vs `Code.gs` found no mismatches (see CLAUDE.md).

## 1. Baseline **[you]** (2 min)
```
cd D:\@Tesis\Claude\desk-robot-page
git add -A
git commit -m "import session page v2"
```

## 2. Deploy the Apps Script relay **[you]** (15 min, from README)
1. Private Drive folder, shared only with you and your teammate. Copy the folder id.
2. script.google.com > new project > paste `apps-script/Code.gs`.
3. Project Settings > Script properties: `FOLDER_ID`, `INVITES` (e.g. `AB12CD,EF34GH`). Optional `MAX_BYTES`, `MAX_USES`.
4. Deploy > Web app: Execute as **Me**, access **Anyone**. Approve Drive permission. Copy the `/exec` URL.
5. Optional for later automation: `npm i -g @google/clasp`, `clasp login`, then in `apps-script/` run `clasp clone <scriptId>`. After that Claude can `clasp push` edits; a new deployment version is still a click in the editor.

Limits to know: one chunk POST carries about 4 MB of base64 JSON, under Apps Script's 50 MB per request. A 400 MB video is about 134 chunks. The resumable session lives 6 hours in CacheService.

## 3. Configure and host the page
1. **[you]** Paste the `/exec` URL into `CONFIG.ENDPOINT` in `index.html`; set `RESEARCHER`, `CONTACT`, `CONSENT_URL` when you have them.
2. **[claude]** Create a GitHub repo and enable Pages (needs your OK once):
   ```
   gh repo create desk-robot-page --public --source=. --push
   gh api -X POST repos/<user>/desk-robot-page/pages -f build_type=legacy -f "source[branch]=main" -f "source[path]=/"
   ```
   The page needs https for camera access; GitHub Pages gives that. The endpoint URL will be visible in the page source, which README already accepts.

## 4. Test matrix (the README's "not tested" list)
| Test | Who | How |
|---|---|---|
| Relay init/chunk/status with a real 100+ MB file, no camera | **[you]** runs, script ready | `scripts/test_upload.py`, commands in 4a |
| Real camera + MediaPipe model download | **[you]** | Open the hosted page with `#fast`, run one session, check `_features.csv` has `face=1` rows |
| Yaw/pitch sign convention | **[you]** then **[claude]** | Turn head left, right, up, down in a `#fast` session; Claude writes `scripts/check_signs.py` that plots yaw/pitch over time from the CSV so you can read the sign |
| Safari / iPhone, Firefox, Android Chrome | **[you]** | One `#fast` session each; note mime (`.mp4` on Safari) and whether upload completes |
| Retry path on the real relay | **[you]** runs, script ready | `--fail-at` and `--lose-reply-at` in 4a |

### 4a. Relay test commands
`scripts/test_upload.py` speaks the same protocol as `uploadBlob()` in `index.html` (3 MiB chunks, base64, text/plain POST). It was verified on 2026-11-16 against `scripts/mock_relay.py` only: rejection checks, 10 MB, both resume paths, and 120 MB all passed with matching md5. It has not run against the real Apps Script yet.

Add a dedicated test code to `INVITES` first (each upload uses one of its `MAX_USES`), then in PowerShell:
```
$env:DESK_ENDPOINT = "https://script.google.com/macros/s/XXX/exec"
$env:DESK_INVITE = "your-test-code"
python scripts/test_upload.py --negative
python scripts/test_upload.py --size-mb 5
python scripts/test_upload.py --size-mb 20 --fail-at 2
python scripts/test_upload.py --size-mb 20 --lose-reply-at 2
python scripts/test_upload.py --size-mb 120
```
Run them in that order; that is 4 uploads, so 4 of the 12 uses. Each run ends with `PASS` or `FAIL` and exit code 0 or 1. After a PASS, open the Drive folder, confirm the `TEST_*_video.webm` file has the printed size, then delete it. `--negative` uploads nothing and uses no quota.

What to expect on the real relay: a few seconds per chunk, so 120 MB (40 chunks) takes minutes, not seconds. If `--negative` reports "reply is not JSON", the web app is not deployed with access = Anyone or the URL is not the `/exec` one.

To rehearse offline: `python scripts/mock_relay.py --invites TEST01`, then use endpoint `http://127.0.0.1:8787/exec` and invite `TEST01`.

## 5. Ethics and consent **[you]**
Settle outside this repo: ITMO ethics approval, whether face video on Google Drive is allowed for your participants, deletion date. Then put the consent text at `CONSENT_URL` and set `SEND_TO` if participants may send files manually.

## 6. Pilot **[you]**, then **[claude]**
Run 2 full sessions (you + teammate) with real invite codes. Check the Drive folder for the three files per code. Remux before analysis:
```
ffmpeg -i in.webm -c copy out.webm
```
Claude then writes the first analysis script: load `_features.csv` + `_events.csv`, align by `t_ms`, summarise face-present ratio per block.

## 7. Recruit
Hand out invite codes, keep the `uploads` sheet restricted, and watch `MAX_USES`.

## Merge into intent-wake (at the end)
When steps 1-6 pass, this folder becomes `intent-wake/collector/` with history kept:
```
cd D:\@Tesis\Claude\intent-wake
git subtree add --prefix=collector ../desk-robot-page main
```
Collected CSVs go to `intent-wake/data/raw/` (never video to any LLM), and `scripts/check_signs.py` plus the analysis script move to `intent-wake/scripts/`. Until then, nothing here depends on intent-wake.
