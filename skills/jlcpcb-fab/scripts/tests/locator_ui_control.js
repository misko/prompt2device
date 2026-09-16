// Exercise the actual shipped selection function with a minimal DOM surface.
// This is a state-transition test; visual usability remains a browser review.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const html = fs.readFileSync(process.argv[2], 'utf8');
class Element {
  constructor() {
    this.children = []; this.textContent = ''; this.value = ''; this.dataset = {}; this.style = {}; this.attributes = {}; this.listeners = {};
    const values = new Set();
    this.classList = {
      toggle: (key, on) => on ? values.add(key) : values.delete(key),
      remove: key => values.delete(key), contains: key => values.has(key)
    };
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; this.textContent = ''; }
  setAttribute(key, value) { this.attributes[key] = value; }
  addEventListener(key, fn) { this.listeners[key] = fn; }
}
function boot(initialHash) {
const parts = [...html.matchAll(/<g class="part" data-ref="([^"]+)">/g)].map(match => {
  const node = new Element(); node.dataset.ref = match[1]; return node;
});
const ids = new Map(['query', 'error', 'ref', 'details', 'pads', 'cross', 'identity', 'side', 'view'].map(id => [id, new Element()]));
ids.get('side').value = 'top';
const context = {
  document: {
    querySelector: selector => ids.get(selector.slice(1)),
    querySelectorAll: selector => { assert.equal(selector, '.part'); return parts; },
    createElement: () => new Element(), createElementNS: () => new Element()
  },
  location: { hash: initialHash }, window: {}, console, Map, Object, String, Math,
  encodeURIComponent, decodeURIComponent
};
vm.createContext(context);
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.runInContext(script, context, {timeout: 5000});
return {parts, ids, context};
}
const {parts, ids, context} = boot('');
const data = context.window.locator.data;
for (const part of data.parts) {
  assert.equal(context.window.locator.select(part.ref), true);
  assert.equal(ids.get('side').value, part.side);
  const shown = parts.filter(node => node.style.display !== 'none');
  assert.deepEqual(shown.map(node => node.dataset.ref).sort(), data.parts.filter(p => p.side === part.side).map(p => p.ref).sort());
  const cross = ids.get('cross').children[0];
  const expectedX = part.side === 'bottom' ? data.frame[0] + data.frame[2] - part.x : part.x;
  assert.equal(cross.attributes.cx, expectedX, 'crosshair must use selected side projection');
  assert.equal(cross.attributes.cy, part.y);
  assert.ok(ids.get('view').textContent.toLowerCase().includes(part.side));
}
for (const side of ['top', 'bottom', 'top']) {
  ids.get('side').value = side;
  ids.get('side').listeners.change({target: ids.get('side')});
  const target = data.parts.find(p => p.side === side);
  if (target) {
    assert.equal(ids.get('ref').textContent, target.ref);
    assert.equal(ids.get('side').value, side);
    assert.equal(parts.filter(node => node.style.display !== 'none').length, data.parts.filter(p => p.side === side).length);
  } else {
    assert.equal(ids.get('ref').textContent, '');
    assert.equal(parts.filter(node => node.style.display !== 'none').length, 0);
    assert.equal(ids.get('view').textContent, 'No components on this side');
  }
}
const valid = parts[0].dataset.ref;
assert.equal(context.window.locator.select(valid), true);
assert.equal(ids.get('ref').textContent, valid);
assert.equal(parts.filter(p => p.classList.contains('selected')).length, 1);
assert.equal(context.window.locator.select('DOES_NOT_EXIST'), false);
assert.ok(ids.get('error').textContent.length > 0);
assert.equal(parts.filter(p => p.classList.contains('selected')).length, 0, 'unknown query retained a body selection');
assert.equal(ids.get('ref').textContent, '', 'unknown query retained the prior identity');
for (const id of ['cross', 'details', 'pads']) assert.equal(ids.get(id).children.length, 0, `unknown query retained ${id}`);
assert.equal(context.location.hash, '', 'unknown query retained prior URL identity');
console.log(`PASS: ${data.parts.length}/${data.parts.length} reference selections; mounted-side visibility and crosshairs; top/bottom/top selector and empty-side control; valid → unknown clears highlight, identity, pads, crosshair and hash`);

// Fresh DOM is essential: unknown-after-valid already has side filtering.
// RED on reviewed candidate1: unknown startup exposes both sides; malformed
// percent escapes throw before the public API is initialized.
const top = data.parts.find(p => p.side === 'top');
const bottom = data.parts.find(p => p.side === 'bottom');
const startupCases = [
  {hash: '', ref: data.hidden[0]}, {hash: '#', ref: data.hidden[0]},
  {hash: '#' + encodeURIComponent(top.ref), ref: top.ref},
  ...(bottom ? [{hash: '#' + encodeURIComponent(bottom.ref), ref: bottom.ref}] : []),
  ...['#DOES_NOT_EXIST', '#%', '#%E0%A4%A', '#%FF'].map(hash => ({hash, ref: null}))
];
const observations = startupCases.map(test => {
  try {
    const fresh = boot(test.hash);
    const visible = fresh.parts.filter(node => node.style.display !== 'none');
    const lookup = new Map(data.parts.map(p => [p.ref, p]));
    const sides = {};
    for (const node of visible) {
      const side = lookup.get(node.dataset.ref).side;
      sides[side] = (sides[side] || 0) + 1;
    }
    return {test, fresh, observed: {initialHash: test.hash, selected: fresh.ids.get('ref').textContent,
      selector: fresh.ids.get('side').value, visible: visible.length, sides,
      view: fresh.ids.get('view').textContent, error: fresh.ids.get('error').textContent,
      crosshairs: fresh.ids.get('cross').children.length, finalHash: fresh.context.location.hash}};
  } catch (error) { return {test, observed: {initialHash: test.hash, exception: String(error)}}; }
});
if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(observations.map(o => o.observed), null, 2));
console.log('Fresh-DOM startup observations: ' + JSON.stringify(observations.map(o => o.observed)));
for (const {test, fresh, observed} of observations) {
  assert.ok(!observed.exception, 'startup must recover from malformed URL decoding: ' + observed.exception);
  if (test.ref) {
    const wanted = data.parts.find(p => p.ref === test.ref);
    assert.equal(observed.selected, wanted.ref);
    assert.equal(observed.selector, wanted.side);
    assert.deepEqual(observed.sides, {[wanted.side]: data.parts.filter(p => p.side === wanted.side).length});
    assert.equal(observed.crosshairs, 1);
  } else {
    assert.equal(observed.visible, 0, 'invalid startup must not expose an uninitialized mounted-side population');
    assert.equal(observed.selected, '');
    assert.equal(observed.crosshairs, 0);
    assert.equal(observed.finalHash, '');
    assert.ok(observed.error.length > 0);
    assert.ok(observed.view.includes('No component selected'));
    for (const id of ['details', 'pads']) assert.equal(fresh.ids.get(id).children.length, 0);
    assert.equal(fresh.parts.filter(p => p.classList.contains('selected')).length, 0);
    // Failed startup still exposes working search and side controls.
    assert.equal(fresh.context.window.locator.select(top.ref), true);
    assert.equal(fresh.ids.get('ref').textContent, top.ref);
    for (const side of ['bottom', 'top']) {
      fresh.ids.get('side').value = side;
      fresh.ids.get('side').listeners.change({target: fresh.ids.get('side')});
      const wanted = data.parts.find(p => p.side === side);
      assert.equal(fresh.ids.get('ref').textContent, wanted ? wanted.ref : '');
      assert.equal(fresh.parts.filter(p => p.style.display !== 'none').length, data.parts.filter(p => p.side === side).length);
    }
  }
}
console.log(`PASS: ${observations.length}/${observations.length} independent fresh-DOM startup cases; valid/default, unknown and malformed URL recovery`);
