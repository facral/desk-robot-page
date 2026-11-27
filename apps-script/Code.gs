// VERSION: drive-direct-4 (2026-11-27). Must match the version shown when you open the /exec URL.
/**
 * Upload relay for the desk-robot session page. It only accepts the two CSV files of a session
 * (events with speech text, and face features); the page sends no video or audio.
 * Deploy as a web app: Execute as = Me, Who has access = Anyone.
 *
 * There are no invite codes: the page is shared publicly. What limits strangers instead: only file
 * names of the form CODE_laptop|phone_events|features.csv, only content that starts with the matching
 * "# session_code=" line, at most MAX_BYTES per file and DAILY_MAX files per day.
 *
 * Script properties (Project Settings > Script properties):
 *   FOLDER_ID  id of the private Drive folder that receives the files (required)
 *   DAILY_MAX  optional files accepted per day, default 200 (one session sends 2)
 *   MAX_BYTES  optional size limit per file, default 3145728 (one chunk, see chunk_)
 *
 * The browser sends text/plain POSTs with a JSON body:
 *   {action:'init',  name, mime, size}                          -> {ok, sid}
 *   {action:'chunk', sid, offset, total, data(base64)}          -> {ok, received}
 *   {action:'status', sid, total}                               -> {ok, received}
 * GET -> {ok, version, full}, where full means today's limit is used up.
 */

var ALLOWED_MIME = ['text/csv'];
var NAME_RE = /^([A-Z0-9]{6})_(laptop|phone)_(events|features)\.csv$/;

function doPost(e) {
  try {
    var b = JSON.parse(e.postData.contents);
    if (b.action === 'init') return out(init_(b));
    if (b.action === 'chunk') return out(chunk_(b));
    if (b.action === 'status') return out(status_(b));
    return out({ ok: false, error: 'action' });
  } catch (err) {
    console.error(err);   // visible under Executions, never sent to the caller
    return out({ ok: false, error: 'server' });
  }
}

function doGet() {
  return out({ ok: true, service: 'desk-robot-upload', version: 'drive-direct-4', full: today_().count >= dailyMax_() });   // bump version on every change
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function props_() { return PropertiesService.getScriptProperties(); }

function dailyMax_() { return Number(props_().getProperty('DAILY_MAX') || 200); }

// Files accepted today, stored as one "date:count" property.
function today_() {
  var day = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var parts = String(props_().getProperty('TODAY') || '').split(':');
  return { day: day, count: parts[0] === day ? Number(parts[1]) : 0 };
}

function init_(b) {
  var p = props_();
  var m = NAME_RE.exec(String(b.name || ''));
  if (!m) return { ok: false, error: 'name' };
  if (ALLOWED_MIME.indexOf(b.mime) < 0) return { ok: false, error: 'mime' };
  var size = Number(b.size);
  var max = Number(p.getProperty('MAX_BYTES') || 3145728);
  if (!(size > 0) || size > max) return { ok: false, error: 'size' };
  try { DriveApp.getFolderById(p.getProperty('FOLDER_ID')); } catch (err) { return { ok: false, error: 'folder' }; }

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var t = today_();
    if (t.count >= dailyMax_()) return { ok: false, error: 'full' };
    p.setProperty('TODAY', t.day + ':' + (t.count + 1));
  } finally {
    lock.releaseLock();
  }

  var sid = Utilities.getUuid();
  CacheService.getScriptCache().put('sess_' + sid, JSON.stringify({ size: size, code: m[1], name: b.name, mime: b.mime, done: false }), 21600);
  log_(m[1], b.name, size, 'init');
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
  if (Utilities.newBlob(bytes).getDataAsString().indexOf('# session_code=' + s.code) !== 0) return { ok: false, error: 'content' };
  DriveApp.getFolderById(props_().getProperty('FOLDER_ID')).createFile(Utilities.newBlob(bytes, s.mime, s.name));
  s.done = true;
  CacheService.getScriptCache().put('sess_' + b.sid, JSON.stringify(s), 21600);
  log_(s.code, s.name, s.size, 'done');
  return { ok: true, received: s.size };
}

function status_(b) {
  var s = session_(b.sid);
  if (!s) return { ok: false, error: 'sid' };
  return { ok: true, received: s.done ? s.size : 0 };
}

// Optional audit trail: a sheet named "uploads" in the spreadsheet this script is bound to, if any.
function log_(code, name, size, event) {
  try {
    var ss = SpreadsheetApp.getActive();
    if (!ss) return;
    var sh = ss.getSheetByName('uploads') || ss.insertSheet('uploads');
    sh.appendRow([new Date(), code, name, size, event]);
  } catch (err) {}
}
