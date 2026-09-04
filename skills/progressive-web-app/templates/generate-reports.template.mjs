// generate-reports.mjs — deterministically render the audit JSON outputs into a single readable report.
// Reads the JSON artifacts in <reports_root>/pwa_scores and writes:
//   PWA_REPORT.md    — GitHub-flavoured markdown tables (intermediate, human-readable)
//   PWA_REPORT.html  — the single ENTRY-POINT deliverable: the same tables + links to the two
//                      Lighthouse HTML reports.
// No AI prose, no network: everything is derived from the JSON data. The timestamp is read from
// verify-app-report.json (not Date.now()) so the same inputs always produce the same output.
import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { resolveReportsDir, readAnchor } from './create-reports-directory.mjs';

const dir = resolveReportsDir();
const readJson = (name) => {
  const p = path.join(dir, name);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; }
};

const responsive = readJson('responsive-audit.json');
const pwa = readJson('pwa-checks.json');
const lh = readJson('lighthouse.report.json');
const lhPwa = readJson('lighthouse-pwa.report.json');
const unified = readJson('verify-app-report.json');

// ---- Build a plain data model (arrays of rows) -----------------------------------------------
const pct = (s) => (s == null ? '—' : Math.round(s * 100));

const lighthouseScores = [];
if (lh?.categories) {
  for (const key of ['performance', 'accessibility', 'best-practices']) {
    if (lh.categories[key]) lighthouseScores.push([lh.categories[key].title || key, pct(lh.categories[key].score)]);
  }
}
if (lhPwa?.categories?.pwa) lighthouseScores.push(['PWA (v11)', pct(lhPwa.categories.pwa.score)]);

const lhMetrics = [];
if (lh?.audits) {
  for (const id of ['first-contentful-paint', 'largest-contentful-paint', 'speed-index', 'total-blocking-time', 'cumulative-layout-shift']) {
    const a = lh.audits[id];
    if (a) lhMetrics.push([a.title || id, a.displayValue ?? String(a.numericValue ?? '—')]);
  }
}

const pwaRows = (pwa?.results ?? []).map((r) => [r.name || r.id, r.ok ? 'PASS' : 'FAIL', shortDetail(r.detail)]);
const pwaPass = (pwa?.results ?? []).filter((r) => r.ok).length;
const pwaTotal = (pwa?.results ?? []).length;

const respRows = (responsive?.results ?? []).map((r) => {
  const d = r.detail || {};
  const off = d.offenders?.widest?.[0];
  const culprit = !r.ok && off ? `${off.tag}${off.cls ? '.' + off.cls.split(' ')[0] : ''} (${off.width}px)` : '';
  const overflow = d.error ? 'load error' : d.overflow ? `+${(d.scrollWidth ?? 0) - (d.clientWidth ?? 0)}px` : 'ok';
  return [r.id?.replace(/^L1-/, '') || r.name, r.ok ? 'PASS' : 'FAIL', overflow, culprit];
});
const respPass = (responsive?.results ?? []).filter((r) => r.ok).length;
const respTotal = (responsive?.results ?? []).length;

const timestamp = unified?.timestamp ?? '(unknown)';
const project = readAnchor().project ?? 'app';

function shortDetail(d) {
  if (!d || typeof d !== 'object') return '';
  if (Array.isArray(d.errors)) return d.errors.length ? `errors: ${d.errors.length}` : '';
  if (d.controller !== undefined) return `controller=${d.controller}, active=${d.active}`;
  if (d.metaTheme) return d.metaTheme;
  if (Array.isArray(d.missing)) return d.missing.length ? `missing: ${d.missing.join(', ')}` : '';
  return '';
}

// ---- Markdown ---------------------------------------------------------------------------------
const mdTable = (headers, rows) =>
  [`| ${headers.join(' | ')} |`, `| ${headers.map(() => '---').join(' | ')} |`, ...rows.map((r) => `| ${r.join(' | ')} |`)].join('\n');

const md = `# PWA Report — ${project}

- Generated: ${timestamp}
- Level 1 (responsive): ${respPass}/${respTotal} · Level 2 (PWA installability): ${pwaPass}/${pwaTotal}

## Lighthouse scores
${mdTable(['Category', 'Score'], lighthouseScores.length ? lighthouseScores : [['—', '—']])}

### Key metrics
${mdTable(['Metric', 'Value'], lhMetrics.length ? lhMetrics : [['—', '—']])}

## Level 2 — PWA installability
${mdTable(['Check', 'Result', 'Detail'], pwaRows.length ? pwaRows : [['—', '—', '—']])}

## Level 1 — Responsive
${mdTable(['Route @ viewport', 'Result', 'Overflow', 'Offending element'], respRows.length ? respRows : [['—', '—', '—', '—']])}

## Full Lighthouse reports
- [Performance / Accessibility / Best-practices](./lighthouse.report.html)
- [PWA category (v11)](./lighthouse-pwa.report.html)
`;
writeFileSync(path.join(dir, 'PWA_REPORT.md'), md);

// ---- HTML (entry point) -----------------------------------------------------------------------
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const badge = (ok) => (ok ? '<span class="ok">PASS</span>' : '<span class="fail">FAIL</span>');
// Rows hold pre-rendered, trusted cell HTML: data cells are escaped via esc(), status via badge().
const htmlTable = (headers, rows) =>
  `<table><thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows
    .map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`)
    .join('')}</tbody></table>`;

const scoreRowsH = lighthouseScores.map(([c, s]) => [esc(c), esc(s)]);
const metricRowsH = lhMetrics.map(([m, v]) => [esc(m), esc(v)]);
const pwaRowsH = (pwa?.results ?? []).map((r) => [esc(r.name || r.id), badge(r.ok), esc(shortDetail(r.detail))]);
const respRowsH = (responsive?.results ?? []).map((r) => {
  const d = r.detail || {};
  const off = d.offenders?.widest?.[0];
  const culprit = !r.ok && off ? `${off.tag}${off.cls ? '.' + off.cls.split(' ')[0] : ''} (${off.width}px)` : '';
  const overflow = d.error ? 'load error' : d.overflow ? `+${(d.scrollWidth ?? 0) - (d.clientWidth ?? 0)}px` : 'ok';
  return [esc((r.id || r.name || '').replace(/^L1-/, '')), badge(r.ok), esc(overflow), esc(culprit)];
});

const pills = [
  `<span class="pill">L1 responsive <b>${respPass}/${respTotal}</b></span>`,
  `<span class="pill">L2 installability <b>${pwaPass}/${pwaTotal}</b></span>`,
  ...lighthouseScores.map(([c, s]) => `<span class="pill">${esc(c)} <b>${esc(s)}</b></span>`),
].join('');

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PWA Report — ${esc(project)}</title>
<style>
  :root { color-scheme: light dark; --line: #8883; --muted: #6b7280; --brand: #0e7c5a; }
  * { box-sizing: border-box; }
  body { font: 15px/1.55 -apple-system, system-ui, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 2.5rem 1rem 4rem; }
  main { max-width: 920px; margin: 0 auto; }
  h1 { margin: 0 0 .25rem; font-size: 1.9rem; letter-spacing: -.02em; }
  h2 { margin: 2.25rem 0 .5rem; font-size: 1.15rem; }
  h3 { margin: 1.25rem 0 .25rem; font-size: .95rem; color: var(--muted); }
  .meta { color: var(--muted); margin: 0 0 1rem; }
  .pills { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0 0 1.5rem; }
  .pill { border: 1px solid var(--line); border-radius: 999px; padding: .28rem .8rem; font-size: .84rem; white-space: nowrap; }
  .pill b { font-weight: 700; }
  table { border-collapse: collapse; width: 100%; margin: .5rem 0; font-size: .92rem; }
  th, td { border: 1px solid var(--line); padding: 7px 11px; text-align: left; vertical-align: top; }
  th { background: color-mix(in srgb, var(--brand) 9%, transparent); font-weight: 600; }
  .ok { color: #0a7f3f; font-weight: 700; } .fail { color: #c0392b; font-weight: 700; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; margin-top: .5rem; }
  .card { display: block; border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; text-decoration: none; color: inherit; transition: border-color .15s ease, transform .15s ease; }
  .card:hover { border-color: var(--brand); transform: translateY(-2px); }
  .card .t { font-weight: 700; font-size: 1rem; }
  .card .s { color: var(--muted); font-size: .85rem; margin: .2rem 0 .7rem; }
  .card .cta { color: var(--brand); font-weight: 600; font-size: .9rem; }
</style></head><body><main>
<h1>PWA Report — ${esc(project)}</h1>
<p class="meta">Generated ${esc(timestamp)}</p>
<div class="pills">${pills}</div>

<h2>Lighthouse scores</h2>
${htmlTable(['Category', 'Score'], scoreRowsH)}
<h3>Key metrics</h3>
${htmlTable(['Metric', 'Value'], metricRowsH)}

<h2>Level 2 — PWA installability</h2>
${htmlTable(['Check', 'Result', 'Detail'], pwaRowsH)}

<h2>Level 1 — Responsive</h2>
${htmlTable(['Route @ viewport', 'Result', 'Overflow', 'Offending element'], respRowsH)}

<h2>Full Lighthouse reports</h2>
<div class="cards">
  <a class="card" href="./lighthouse.report.html"><div class="t">Lighthouse — Quality</div><div class="s">Performance · Accessibility · Best-practices (v12)</div><div class="cta">Open full report →</div></a>
  <a class="card" href="./lighthouse-pwa.report.html"><div class="t">Lighthouse — PWA</div><div class="s">Classic PWA category (v11)</div><div class="cta">Open full report →</div></a>
</div>
</main></body></html>`;
writeFileSync(path.join(dir, 'PWA_REPORT.html'), html);

console.log(`Wrote ${path.join(dir, 'PWA_REPORT.md')}`);
console.log(`Wrote ${path.join(dir, 'PWA_REPORT.html')}`);
