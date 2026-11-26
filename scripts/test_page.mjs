// Self-check of the risky pure logic in index.html: text table, cases, name calling, routing, corrections.
// Run: node scripts/test_page.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8').replace(/\r\n/g, '\n');
const block = (from, to) => html.slice(html.indexOf(from), html.indexOf(to));
const P = new Function(block('const TX = {', '\n/* PURE-START') + block('\n/* PURE-START', '/* PURE-END */') +
  'return { TX, CASES, afterName, route, routeAlts, DONE, YES, NOTME, CORRECT, norm };')();
const { TX, CASES, afterName, route, routeAlts } = P;
const LANGS = ['id', 'en', 'ru'];

for (const [key, row] of Object.entries(TX)) {
  assert.equal(row.length, 3, key + ': needs Indonesian, English and Russian');
  const holes = s => (s.match(/\{\w+\}/g) || []).sort().join();
  assert.ok(row.every(s => s && holes(s) === holes(row[0])), key + ': empty text or different {placeholders}');
}

// Every case is complete in all languages, has one culprit among three suspects, and every fact is reachable.
for (const c of CASES) {
  const who = c.facts.filter(f => f.who);
  assert.equal(who.length, 3, c.id + ': three suspects');
  assert.ok(who.some(f => f.id === c.culprit), c.id + ': culprit is a suspect');
  assert.equal(c.facts[0].who !== undefined && c.facts.some(f => f.name), true, c.id + ': examples need a suspect first and a named fact');
  for (const l of LANGS) {
    assert.ok(c.story[l] && c.solved[l] && c.clues[l].length === 3, c.id + ' ' + l + ': story, solution, three clues');
    for (const f of c.facts) assert.ok(f.say[l] && (f.who || f.name)[l], c.id + '.' + f.id + ' ' + l);
    for (const f of who) assert.equal(route('di mana ' + f.who[l], 'A', c), 'fact:' + f.id, c.id + ': ' + f.who[l]);
  }
  for (const f of c.facts.filter(f => f.k)) {
    const word = f.k.split('|')[0];
    assert.equal(route('ceritakan soal ' + word, 'A', c), 'fact:' + f.id, c.id + ': ' + word);
  }
}
const cake = CASES[0];
assert.equal(route('где был бориса', 'A', cake), 'fact:b', 'Russian case ending');
assert.equal(route('apa yang terjadi jam tiga di dapur', 'A', cake), 'fact:kitchen', '"jam tiga" is not a clock question');
assert.equal(route('jam berapa sekarang', 'A', cake), 'time');
assert.equal(route('beri aku petunjuk', 'A', cake), 'clue');
assert.equal(route('ganti kasus', 'B', cake), 'swap');
assert.equal(route('beri aku petunjuk', 'C', null), 'free', 'no clues outside a case');
assert.equal(route('dengarkan aku', 'A', cake), 'free', 'listener mode only in free time');
assert.equal(route('dengarkan aku', 'C', null), 'listen');
assert.equal(route('сколько еще осталось', 'C', null), 'left');
assert.equal(route('saran dong', 'A', CASES[5]), 'free', 'Sarah is matched as a whole word only');
assert.deepEqual(routeAlts(['xyz', 'dimana bima'], 'A', cake), ['fact:b', 'dimana bima'], 'second guess is used');

assert.equal(afterName('Budi, jam berapa sekarang?', 'Budi'), 'jam berapa sekarang');
assert.equal(afterName('budy jam berapa', 'Budi'), 'jam berapa', 'one letter off still counts');
assert.equal(afterName('jam berapa sekarang', 'Budi'), null, 'no name, no call');
assert.equal(afterName('Бадди, который час', 'Бадди'), 'который час');

const n = P.norm;
assert.ok(P.CORRECT.test(n('Salah, harusnya Bima')) && P.CORRECT.test(n('Неправильно, должно быть Борис')) && P.CORRECT.test(n('wrong, it should be Bella')));
assert.ok(P.NOTME.test(n('aku bukan ngomong sama kamu')) && P.NOTME.test(n('nggak ngomong ke kamu')) && P.NOTME.test(n("I wasn't talking to you")) && P.NOTME.test(n('Я говорю не с тобой')));
assert.ok(!P.NOTME.test(n('bukan, kamu salah, harusnya Bima')), 'a correction is not a not-me');
assert.ok(P.DONE.test(n('Selesai.')) && P.DONE.test(n('Готово')) && P.YES.test(n('Да, давай')));
console.log('PASS', Object.keys(TX).length, 'strings,', CASES.length, 'cases, routing and correction checks');
