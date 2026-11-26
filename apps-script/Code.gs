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
 *   MAX_BYTES  optional size limit per file, default 20000000
 *   MAX_USES   optional uploads allowed per invite code, default 12
 *              (one session uploads 2 files, so 12 allows retries and a second device)
 *
 * The browser sends text/plain POSTs with a JSON body:
 *   {action:'init',  invite, name, mime, size}                  -> {ok, sid}
 *   {action:'chunk', sid, offset, total, data(base64)}          -> {ok, received}
 *   {action:'status', sid, total}                               -> {ok, received}
 *
 * Chunk size must be a multiple of 262144 bytes except for the last chunk.
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
    return out({ ok: false, error: 'server' });
  }
}

function doGet() {
  return out({ ok: true, service: 'desk-robot-upload' });
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
  var max = Number(p.getProperty('MAX_BYTES') || 20000000);
  if (!(size > 0) || size > max) return { ok: false, error: 'size' };
  if (!SpreadsheetApp.getActive()) return { ok: false, error: 'sheet' };   // no sheet = no code-to-session record

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

  var res = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable', {
    method: 'post',
    contentType: 'application/json; charset=UTF-8',
    headers: {
      Authorization: 'Bearer ' + ScriptApp.getOAuthToken(),
      'X-Upload-Content-Type': b.mime,
      'X-Upload-Content-Length': String(size)
    },
    payload: JSON.stringify({ name: b.name, parents: [p.getProperty('FOLDER_ID')] }),
    muteHttpExceptions: true,
    followRedirects: false
  });
  if (res.getResponseCode() !== 200) return { ok: false, error: 'drive' };
  var headers = res.getAllHeaders();
  var url = headers['Location'] || headers['location'];
  if (!url) return { ok: false, error: 'drive' };

  var sid = Utilities.getUuid();
  CacheService.getScriptCache().put('sess_' + sid, JSON.stringify({ url: url, size: size, invite: invite, name: b.name }), 21600);
  log_(invite, b.name, size, 'init');
  return { ok: true, sid: sid };
}

function session_(sid) {
  var raw = CacheService.getScriptCache().get('sess_' + sid);
  return raw ? JSON.parse(raw) : null;
}

function chunk_(b) {
  var s = session_(b.sid);
  if (!s) return { ok: false, error: 'sid' };
  var offset = Number(b.offset), total = Number(b.total);
  if (total !== s.size) return { ok: false, error: 'total' };
  var bytes = Utilities.base64Decode(b.data);
  if (!bytes.length) return { ok: false, error: 'empty' };
  var last = offset + bytes.length - 1;
  var res = UrlFetchApp.fetch(s.url, {
    method: 'put',
    contentType: 'application/octet-stream',
    headers: { 'Content-Range': 'bytes ' + offset + '-' + last + '/' + total },
    payload: bytes,
    muteHttpExceptions: true,
    followRedirects: false
  });
  var code = res.getResponseCode();
  if (code === 200 || code === 201) {
    log_(s.invite, s.name, s.size, 'done');
    return { ok: true, received: total };
  }
  if (code === 308) return { ok: true, received: received_(res) };
  return { ok: false, error: 'drive' };
}

function status_(b) {
  var s = session_(b.sid);
  if (!s) return { ok: false, error: 'sid' };
  var res = UrlFetchApp.fetch(s.url, {
    method: 'put',
    contentType: 'application/octet-stream',
    headers: { 'Content-Range': 'bytes */' + s.size },
    payload: '',
    muteHttpExceptions: true,
    followRedirects: false
  });
  var code = res.getResponseCode();
  if (code === 200 || code === 201) return { ok: true, received: s.size };
  if (code === 308) return { ok: true, received: received_(res) };
  return { ok: false, error: 'drive' };
}

// Drive answers 308 with "Range: bytes=0-N" for the bytes it holds; no Range header means none yet.
function received_(res) {
  var h = res.getAllHeaders();
  var range = h['Range'] || h['range'];
  if (!range) return 0;
  var m = /bytes=0-(\d+)/.exec(range);
  return m ? Number(m[1]) + 1 : 0;
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
