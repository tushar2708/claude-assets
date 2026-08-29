// Resolves the PWA audit reports directory from the project's anchor file.
// The anchor (ai_skill_anchors/pwa.json at the project root) holds "reports_root"; reports go to
// <project-root>/<reports_root>/pwa_scores. Scripts MUST use this — never a hardcoded, root-level,
// or cwd-relative folder. If the anchor is missing, fail loudly so the user configures it.
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Walk up from this file to the project root — the nearest ancestor containing ai_skill_anchors/pwa.json.
function findAnchor() {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  for (;;) {
    const candidate = path.join(dir, 'ai_skill_anchors', 'pwa.json');
    if (existsSync(candidate)) return { anchorPath: candidate, projectRoot: dir };
    const parent = path.dirname(dir);
    if (parent === dir) return null; // reached the filesystem root
    dir = parent;
  }
}

export function readAnchor() {
  const found = findAnchor();
  if (!found) {
    throw new Error('ai_skill_anchors/pwa.json not found. Create it at the project root with a "reports_root" key.');
  }
  let data;
  try {
    data = JSON.parse(readFileSync(found.anchorPath, 'utf8'));
  } catch {
    throw new Error('ai_skill_anchors/pwa.json is not valid JSON.');
  }
  return { ...data, _projectRoot: found.projectRoot };
}

export function resolveReportsDir() {
  const a = readAnchor();
  if (!a.reports_root) {
    throw new Error(
      'ai_skill_anchors/pwa.json has no "reports_root". Add it (a path relative to the project root). ' +
        'Do NOT default to a root-level or cwd-relative folder.',
    );
  }
  return path.resolve(a._projectRoot, a.reports_root, 'pwa_scores');
}
