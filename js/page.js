/* What are the odds of a white Christmas where you live? 116 UK towns on a plain MapLibre base map (OpenFreeMap Positron),
 * coloured by the share of Christmas Days with snow lying (more than 1 cm), falling, or both, for all years or one decade.
 * Popups show each town's Christmas calendar, 1940 to 2025. Data: Open-Meteo (ERA5, ERA5-Land), CC BY 4.0.
 * Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const RAMP = ['#DCE7EF', '#9EC2DE', '#4F8DC3', '#1D4F86', '#0B2447'];
  const CODE = { '0': '#E9ECEF', '1': '#9FC3E0', '2': '#4C86BE', '3': '#0E2D57', '4': '#F4F1EA', '5': '#C9D7E3' };
  const DECS = [null, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020];
  const NAME = { l: 'snow lying', f: 'snow falling', b: 'snow falling and lying' };
  let map = null, D = null, mode = qs.get('mode') || 'l', dec = null;
  if (!NAME[mode]) mode = 'l';
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));

  // value for a town under the current mode and period: share (%) or null when no data
  function val(t) {
    if (dec === null) return mode === 'l' ? t.l : mode === 'f' ? t.f : t.b;
    const d = t.d[String(dec)]; if (!d) return null;
    const n = d[2];
    if (mode === 'f') return 100 * d[0] / n;
    if (d[1] === null) return null;
    if (mode === 'l') return 100 * d[1] / n;
    // both: count from the strip
    const i0 = dec - D.y0; let k = 0;
    for (let i = i0; i < i0 + n; i++) if (t.s[i] === '3') k++;
    return 100 * k / n;
  }
  function counts(t) {
    const c = { f: 0, l: 0, b: 0, n: 0, nl: 0 }; const i0 = dec === null ? 0 : dec - D.y0, i1 = dec === null ? t.s.length : Math.min(t.s.length, i0 + 10);
    for (let i = i0; i < i1; i++) { const x = t.s[i]; c.n++; if (x === '1' || x === '3' || x === '5') c.f++; if (x === '2' || x === '3') c.l++; if (x === '3') c.b++; if (x < '4') c.nl++; }
    return c;
  }
  function feats() {
    return { type: 'FeatureCollection', features: D.t.map((t, i) => { const v = val(t); return { type: 'Feature', properties: { i, n: t.n, v: v === null ? -1 : v, z: v === 0 ? 1 : 0, lab: v === null ? `${t.n}` : `${t.n} ${Math.round(v)}%` }, geometry: { type: 'Point', coordinates: [t.lo, t.la] } }; }) };
  }
  function vmax() { return mode === 'f' ? 30 : mode === 'b' ? 15 : 30; }
  function colorExpr() {
    const m = vmax();
    return ['case', ['<', ['get', 'v'], 0], '#C9CED3', ['interpolate', ['linear'], ['get', 'v'], 0, RAMP[0], m * 0.25, RAMP[1], m * 0.5, RAMP[2], m * 0.75, RAMP[3], m, RAMP[4]]];
  }
  function key() {
    const per = dec === null ? (mode === 'f' ? `${D.y0} to ${D.y1}` : `${D.yl0} to ${D.y1}`) : (dec === 2020 ? '2020 to 2025' : `the ${dec}s`);
    document.getElementById('keyTitle').textContent = `Christmas Days with ${NAME[mode]}, ${per}`;
    document.getElementById('keyBar').style.background = `linear-gradient(90deg,${RAMP.join(',')})`;
    const m = vmax(); document.getElementById('keyEnds').innerHTML = `<span>0%</span><span>${m / 2}%</span><span>${m}%+</span>`;
    document.querySelectorAll('.chip[data-m]').forEach(x => x.setAttribute('aria-pressed', x.dataset.m === mode));
    document.getElementById('decLab').textContent = dec === null ? 'All years' : dec === 2020 ? '2020 to 2025' : `${dec}s`;
    const note = document.getElementById('noData');
    const nd = dec === 1940 && mode !== 'f';
    if (nd && !note) { const p = document.createElement('div'); p.id = 'noData'; p.className = 'row'; p.style.color = '#B3412F'; p.textContent = 'No lying-snow data before 1950 (grey dots).'; document.getElementById('keys').appendChild(p); }
    if (!nd && note) note.remove();
  }
  function refresh() { map.getSource('t').setData(feats()); map.setPaintProperty('pts', 'circle-color', colorExpr()); key(); }
  function strip(t) {
    const w = 290, cols = 43, cw = w / cols, ch = 9;
    let s = `<svg class="strip" width="${w}" height="${2 * (ch + 2) + 14}" viewBox="0 0 ${w} ${2 * (ch + 2) + 14}" role="img" aria-label="Christmas Days ${D.y0} to ${D.y1} in ${esc(t.n)}">`;
    for (let i = 0; i < t.s.length; i++) {
      const r = Math.floor(i / cols), c = i % cols, y = D.y0 + i;
      const lab = { '0': 'no snow', '1': 'snow fell', '2': 'snow lying', '3': 'snow fell and lay', '4': 'no snow fell (lying snow unknown)', '5': 'snow fell (lying snow unknown)' }[t.s[i]];
      s += `<rect x="${(c * cw + 0.5).toFixed(1)}" y="${r * (ch + 2)}" width="${(cw - 1).toFixed(1)}" height="${ch}" fill="${CODE[t.s[i]]}"><title>${y}: ${lab}</title></rect>`;
    }
    s += `<text x="0" y="${2 * (ch + 2) + 11}" font-size="10" fill="#5E6B78">rows: ${D.y0} to ${D.y0 + cols - 1}, ${D.y0 + cols} to ${D.y1}</text></svg>`;
    return s;
  }
  function popup(t) {
    const c = counts(t), per = dec === null ? '' : (dec === 2020 ? ' (2020 to 2025)' : ` (${dec}s)`);
    let h = `<b class="t">${esc(t.n)}</b><div class="nt">${esc(t.na)} · town ${t.el} m · reanalysis cell about ${t.ce} m on average</div>`;
    h += `<table><tr><td>Snow lying${per}</td><td><b>${c.nl ? c.l + ' of ' + c.nl : 'no data'}</b>${c.nl ? ` (${Math.round(100 * c.l / c.nl)}%)` : ''}</td></tr>`;
    h += `<tr><td>Snow falling${per}</td><td><b>${c.f} of ${c.n}</b> (${Math.round(100 * c.f / c.n)}%)</td></tr>`;
    h += `<tr><td>Both${per}</td><td>${c.nl ? c.b + ' of ' + c.nl : 'no data'}</td></tr>`;
    h += `<tr><td>Last lying</td><td>${t.ll || 'never since 1950'}</td></tr><tr><td>Last falling</td><td>${t.fl || 'never'}</td></tr>`;
    h += `<tr><td>Christmas top temp.</td><td>${t.tx.toFixed(1)}°C on average</td></tr></table>`;
    h += strip(t);
    h += `<div class="nt"><span class="sw" style="background:${CODE['3']}"></span>fell and lay <span class="sw" style="background:${CODE['2']}"></span>lying <span class="sw" style="background:${CODE['1']}"></span>fell <span class="sw" style="background:${CODE['5']}"></span>fell, 1940s</div>`;
    if (t.ce - t.el > 100) h += `<p class="nt">The reanalysis cell around ${esc(t.n)} is much higher than the town, so lying snow here partly reflects the hills.</p>`;
    else if (t.l >= 50) h += `<p class="nt">The reanalysis cell around ${esc(t.n)} takes in mountain slopes, and the model tends to put too much snow on hills, so read this as the odds for the surrounding area, not the town centre.</p>`;
    h += `<p class="nt">Source: Open-Meteo Historical Weather API (ERA5, ERA5-Land; CC BY 4.0). Lying snow: more than 1 cm on 25 December; falling: any snowfall in the cell.</p>`;
    new maplibregl.Popup({ maxWidth: '330px', anchor: small ? 'bottom' : undefined }).setLngLat([t.lo, t.la]).setHTML(h).addTo(map);
  }
  function setup() {
    map.addSource('t', { type: 'geojson', data: feats(), attribution: 'Snow: Open-Meteo (ERA5, ERA5-Land), CC BY 4.0' });
    map.addLayer({ id: 'pts', type: 'circle', source: 't', filter: ['==', ['get', 'z'], 0], paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, small ? 5 : 6.5, 8, 10, 13, 14], 'circle-color': colorExpr(), 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.4 } });
    map.addLayer({ id: 'zero', type: 'circle', source: 't', filter: ['==', ['get', 'z'], 1], paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, small ? 4.5 : 5.5, 8, 9, 13, 13], 'circle-color': '#FFFFFF', 'circle-stroke-color': '#6E7F90', 'circle-stroke-width': 1.6 } });
    map.addLayer({ id: 'lbl', type: 'symbol', source: 't', minzoom: 6, layout: { 'text-field': ['get', 'lab'], 'text-size': 11.5, 'text-font': ['Noto Sans Regular'], 'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-optional': true }, paint: { 'text-color': '#1F2A36', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } });
    ['pts', 'zero'].forEach(l => { map.on('click', l, e => popup(D.t[e.features[0].properties.i])); map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    const vis = (ids, v) => ids.forEach(id => map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none'));
    document.getElementById('lyP').addEventListener('change', e => vis(['pts'], e.target.checked));
    document.getElementById('lyZ').addEventListener('change', e => vis(['zero'], e.target.checked));
    document.getElementById('lyL').addEventListener('change', e => vis(['lbl'], e.target.checked));
    const baseSym = map.getStyle().layers.filter(l => l.type === 'symbol' && l.id !== 'lbl').map(l => l.id);
    document.getElementById('lyB').addEventListener('change', e => vis(baseSym, e.target.checked));
    document.querySelectorAll('.chip[data-m]').forEach(b => b.addEventListener('click', () => { mode = b.dataset.m; refresh(); }));
    const dr = document.getElementById('dec');
    dr.addEventListener('input', () => { dec = DECS[+dr.value]; refresh(); });
    const d0 = +qs.get('decade'); if (DECS.includes(d0)) { dec = d0; dr.value = DECS.indexOf(d0); }
    refresh();
  }
  function go(i) {
    const t = D.t[i]; fold(true);
    map.flyTo({ center: [t.lo, t.la], zoom: small ? 8 : 8.5, duration: 1200, offset: [0, Math.round(map.getContainer().clientHeight * (small ? 0.3 : 0.22))] });
    map.once('moveend', () => popup(t));
  }
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug'); let items = [], k = -1;
    const idx = D.t.map((t, i) => ({ t: t.n, nn: norm(t.n), i, s: t.na }));
    const show = () => { const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1; if (v.length < 2) { sug.style.display = 'none'; return; }
      items = idx.filter(x => x.nn.startsWith(v)).concat(idx.filter(x => !x.nn.startsWith(v) && v.length > 2 && x.nn.includes(v))).slice(0, 12);
      items.forEach((it, j) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(it.t)} <span>${esc(it.s)}</span>`; li.addEventListener('mousedown', e => { e.preventDefault(); pick(j); }); sug.appendChild(li); });
      if (!items.length) { const li = document.createElement('li'); li.textContent = 'Not one of the 116 towns'; sug.appendChild(li); }
      sug.style.display = 'block'; };
    const pick = j => { const it = items[j]; if (!it) return; q.value = it.t; sug.style.display = 'none'; go(it.i); };
    q.addEventListener('input', show);
    q.addEventListener('keydown', e => { const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show(); pick(k < 0 ? 0 : k); } else if (e.key === 'Escape') sug.style.display = 'none'; });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }
  fetch('data/site.json').then(r => r.json()).then(d => {
    D = d;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { bounds: [[-8.3, 49.9], [1.9, 60.3]], fitBoundsOptions: { padding: small ? { top: 110, bottom: 70, left: 10, right: 10 } : { top: 40, bottom: 70, left: 360, right: 60 } } };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 14 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res(m0)); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(mm => {
    map = mm; window.__map = mm;
    mm.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    mm.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    mm.once('idle', foldAt); setTimeout(foldAt, 1500);
    setup(); setupSearch();
    if (qs.get('town')) { const i = D.t.findIndex(t => norm(t.n) === norm(qs.get('town'))); if (i >= 0) go(i); }
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov-top,.lp,.keys,.tl,.mfs-btn,.maplibregl-ctrl,.maplibregl-popup')) return; fold(true); }, { capture: true, passive: true, once: true });
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
