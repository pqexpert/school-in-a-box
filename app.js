'use strict';
const el = id => document.getElementById(id);
const storageKey = 'school-in-a-box-notes-v1';
let catalog, selected, pendingImport;
function readNotes() {
  try {
    const value = JSON.parse(localStorage.getItem(storageKey) || '{}');
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch { return {}; }
}
function option(value, text) {
  const node = document.createElement('option'); node.value = value; node.textContent = text; return node;
}
function noteKey(d) { return `${el('campus').value}:${d.id}`; }
function campusContext() {
  const campus = catalog.campuses.find(c => c.id === el('campus').value);
  el('campus-context').textContent = campus.context;
  el('rhythm').textContent = `Planning context: ${campus.name}. Suggested rhythm: ${campus.rhythm}`;
}
function show(d) {
  selected = d;
  el('title').textContent = d.title;
  el('kind').textContent = d.collection === 'teacher' ? 'Teacher guide · Includes answers' : d.collection === 'student' ? 'Student activity' : 'School planning template';
  el('status').textContent = `${d.review_status} · CC BY 4.0`;
  el('source').href = './' + d.path;
  el('content').textContent = d.content;
  campusContext();
  const note = readNotes()[noteKey(d)] || {};
  el('notes').value = note.text || '';
  el('complete').checked = !!note.complete;
  el('complete').parentElement.hidden = d.collection === 'planning';
  el('saved').textContent = 'Notes stay in this browser. Export for backup; clear on shared computers.';
  document.querySelectorAll('#library button').forEach(b => b.setAttribute('aria-current', String(b.dataset.id === d.id)));
}
function courseOptions() {
  const course = catalog.courses.find(c => c.id === el('course').value);
  el('week').replaceChildren(option('all', 'All available weeks'), ...course.weeks.map(w => option(String(w.number), `Week ${w.number} · ${w.title}`)));
  el('level').replaceChildren(option('all', 'All levels'), ...course.levels.map(l => option(l.id, `${l.id} · ${l.name}`)));
}
function filter() {
  campusContext();
  const q = el('search').value.trim().toLocaleLowerCase();
  const planning = el('collection').value === 'planning';
  for (const id of ['week', 'level', 'language', 'course']) el(id).disabled = planning;
  const visible = catalog.documents.filter(d => d.collection === el('collection').value &&
    (planning || (d.course === el('course').value &&
      (el('week').value === 'all' || d.week === Number(el('week').value)) &&
      (el('level').value === 'all' || d.levels.includes(el('level').value)) &&
      (el('language').value === 'all' || d.language === el('language').value))) &&
    (d.title + ' ' + d.content).toLocaleLowerCase().includes(q));
  el('library').replaceChildren();
  el('count').textContent = `${visible.length} documents`;
  for (const d of visible) {
    const button = document.createElement('button'); button.textContent = d.title; button.dataset.id = d.id;
    button.addEventListener('click', () => show(d)); el('library').append(button);
  }
  el('reader').hidden = !visible.length;
  if (visible.length) show(visible.find(d => d.id === selected?.id) || visible[0]);
  else selected = undefined;
}
function save() {
  if (!selected) return;
  try {
    const notes = readNotes(); notes[noteKey(selected)] = {title: selected.title, campus: el('campus').value,
      text: el('notes').value, complete: el('complete').checked, updated: new Date().toISOString()};
    localStorage.setItem(storageKey, JSON.stringify(notes));
    el('saved').textContent = 'Saved in this browser on this device.';
  } catch { el('saved').textContent = 'Storage unavailable. Export your current notes before leaving.'; }
}
for (const id of ['search', 'collection', 'week', 'level', 'language', 'campus']) {
  el(id).addEventListener(id === 'search' ? 'input' : 'change', filter);
}
el('course').addEventListener('change', () => { courseOptions(); filter(); });
el('notes').addEventListener('input', save); el('complete').addEventListener('change', save);
el('print').addEventListener('click', () => window.print());
el('export').addEventListener('click', () => {
  const notes = readNotes();
  if (selected) notes[noteKey(selected)] = {title: selected.title, campus: el('campus').value, text: el('notes').value, complete: el('complete').checked};
  const url = URL.createObjectURL(new Blob([JSON.stringify(notes, null, 2)], {type: 'application/json'}));
  const a = document.createElement('a'); a.href = url; a.download = 'school-in-a-box-notes.json'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
el('import').addEventListener('change', async event => {
  pendingImport = undefined; el('confirm-import').hidden = true;
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 1024 * 1024) throw Error('File exceeds 1 MB');
    const incoming = JSON.parse(await file.text());
    if (!incoming || typeof incoming !== 'object' || Array.isArray(incoming)) throw Error('Expected a notes object');
    const validKeys = new Set(catalog.campuses.flatMap(c => catalog.documents.map(d => `${c.id}:${d.id}`)));
    const entries = Object.entries(incoming);
    if (!entries.length || entries.some(([key, n]) => !validKeys.has(key) || !n || typeof n.text !== 'string' || n.text.length > 100000 || typeof n.complete !== 'boolean')) throw Error('Unknown lesson or invalid note');
    pendingImport = Object.fromEntries(entries.map(([key, n]) => [key, {text: n.text, complete: n.complete}]));
    const existing = readNotes(); const overlaps = entries.filter(([key]) => Object.hasOwn(existing, key)).length;
    el('import-status').textContent = `Review: import ${entries.length} notes. ${overlaps} existing notes will be replaced; other notes remain. Confirm to proceed.`;
    el('confirm-import').hidden = false;
  } catch (error) { el('import-status').textContent = `Import rejected: ${error.message}. No notes changed.`; }
  event.target.value = '';
});
el('confirm-import').addEventListener('click', () => {
  if (!pendingImport) return;
  try {
    localStorage.setItem(storageKey, JSON.stringify({...readNotes(), ...pendingImport}));
    pendingImport = undefined; el('confirm-import').hidden = true; el('import-status').textContent = 'Notes imported into this browser.'; if (selected) show(selected);
  } catch { el('import-status').textContent = 'Storage unavailable. Import did not complete.'; }
});
el('clear').addEventListener('click', () => {
  if (!window.confirm('Clear all School in a Box notes and practice markers in this browser? Export a backup first if needed.')) return;
  try { localStorage.removeItem(storageKey); if (selected) show(selected); el('saved').textContent = 'All local notes cleared.'; }
  catch { el('saved').textContent = 'Unable to clear browser storage.'; }
});
fetch('./catalog.json').then(response => { if (!response.ok) throw Error('Library unavailable'); return response.json(); })
  .then(data => {
    catalog = data;
    el('campus').replaceChildren(...data.campuses.map(c => option(c.id, c.name)));
    el('course').replaceChildren(...data.courses.map(c => option(c.id, c.title)));
    courseOptions(); filter();
  }).catch(() => { el('count').textContent = 'Unable to load library. Check catalog build and local server, then reload.'; el('reader').hidden = true; });
