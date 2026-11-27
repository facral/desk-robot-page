// VERSION: drive-direct-2 (2026-11-27). Must match the version shown when you open the /exec URL.
/**
 * Upload relay for the desk-robot session page. It only accepts the two CSV files of a session
 * (events with speech text, and face features); the page sends no video or audio.
 * Create it from a Google Sheet (Extensions > Apps Script), not at script.google.com: the sheet
 * "uploads" is the only link between an invite code and a session, and init refuses without it.
 * Deploy as a web app: Execute as = Me, Who has access = Anyone.
 *
 * Script properties to set (Project Settings > Script properties):
 *   FOLDER_ID  id of the private Drive folder that receives the files
 *   INVITES    comma-separated invite codes, for example: AB12CD,EF34GH
 *   MAX_BYTES  optional size limit per file, default 3145728 (one chunk, see chunk_)
 *   MAX_USES   optional uploads allowed per invite code, default 12
 *              (one session uploads 2 files, so 12 allows retries and a second device)
 *
 * The browser sends text/plain POSTs with a JSON body:
 *   {action:'init',  invite, name, mime, size}                  -> {ok, sid}
 *   {action:'chunk', sid, offset, total, data(base64)}          -> {ok, received}
 *   {action:'status', sid, total}                               -> {ok, received}
 *
 * Each file arrives in a single chunk at offset 0; the relay writes it to the folder with DriveApp.
 * Keep the mapping invite -> file names (sheet "uploads") private: it is the only link between a person and a recording.
 */

var ALLOWED_MIME = ['text/csv'];
var NAME_RE = /^[A-Za-z0-9_.-]{1,80}$/;

function doPost(e) {
  try {
    var b = JSON.parse(e.postData.contents);
    if (b.action === 'init') return out(init_(b));
    if (b.action === 'chunk') return out(chunk_(b));
    if (b.action === 'status') return out(status_(b));
    return out({ ok: false, error: 'action' });
  } catch (err) {
    return out({ ok: false, error: 'server', detail: String(err).slice(0, 200) });
  }
}

function doGet() {
  return out({ ok: true, service: 'desk-robot-upload', version: 'drive-direct-2' });   // bump on every change, to see which code a deployment runs
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function props_() { return PropertiesService.getScriptProperties(); }

function init_(b) {
  var p = props_();
  var invites = (p.getProperty('INVITES') || '').split(',').map(function (s) { return s.trim(); }).filter(String);
  var invite = String(b.invite || '').trim();
  if (invites.indexOf(invite) < 0) return { ok: false, error: 'invite' };
  if (!NAME_RE.test(String(b.name || ''))) return { ok: false, error: 'name' };
  if (ALLOWED_MIME.indexOf(b.mime) < 0) return { ok: false, error: 'mime' };
  var size = Number(b.size);
  var max = Number(p.getProperty('MAX_BYTES') || 3145728);
  if (!(size > 0) || size > max) return { ok: false, error: 'size' };
  if (!SpreadsheetApp.getActive()) return { ok: false, error: 'sheet' };   // no sheet = no code-to-session record
  try { DriveApp.getFolderById(p.getProperty('FOLDER_ID')); } catch (err) { return { ok: false, error: 'folder' }; }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var key = 'USES_' + invite;
    var uses = Number(p.getProperty(key) || 0);
    if (uses >= Number(p.getProperty('MAX_USES') || 12)) return { ok: false, error: 'uses' };
    p.setProperty(key, String(uses + 1));
  } finally {
    lock.releaseLock();
  }

  var sid = Utilities.getUuid();
  CacheService.getScriptCache().put('sess_' + sid, JSON.stringify({ size: size, invite: invite, name: b.name, mime: b.mime, done: false }), 21600);
  log_(invite, b.name, size, 'init');
  return { ok: true, sid: sid };
}

function session_(sid) {
  var raw = CacheService.getScriptCache().get('sess_' + sid);
  return raw ? JSON.parse(raw) : null;
}

// shortcut: a whole file must arrive in one chunk (MAX_BYTES = the page's 3 MiB CHUNK); session CSVs are
// well under 1 MB. For bigger files, go back to a Drive resumable upload (needs the Drive API service).
function chunk_(b) {
  var s = session_(b.sid);
  if (!s) return { ok: false, error: 'sid' };
  if (Number(b.total) !== s.size) return { ok: false, error: 'total' };
  if (s.done) return { ok: true, received: s.size };   // a retry after a lost reply: the file already exists
  if (Number(b.offset) !== 0) return { ok: false, error: 'offset' };
  var bytes = Utilities.base64Decode(b.data);
  if (bytes.length !== s.size) return { ok: false, error: 'size' };
  DriveApp.getFolderById(props_().getProperty('FOLDER_ID')).createFile(Utilities.newBlob(bytes, s.mime, s.name));
  s.done = true;
  CacheService.getScriptCache().put('sess_' + b.sid, JSON.stringify(s), 21600);
  log_(s.invite, s.name, s.size, 'done');
  return { ok: true, received: s.size };
}

function status_(b) {
  var s = session_(b.sid);
  if (!s) return { ok: false, error: 'sid' };
  return { ok: true, received: s.done ? s.size : 0 };
}

// Optional audit trail: a sheet named "uploads" in the spreadsheet bound to this script.
function log_(invite, name, size, event) {
  try {
    var ss = SpreadsheetApp.getActive();
    if (!ss) return;
    var sh = ss.getSheetByName('uploads') || ss.insertSheet('uploads');
    sh.appendRow([new Date(), invite, name, size, event]);
  } catch (err) {}
}
