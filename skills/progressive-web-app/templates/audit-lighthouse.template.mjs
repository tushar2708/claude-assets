// scripts/verify-pwa/audit-lighthouse.mjs
// Lighthouse quality audit (performance, accessibility, best-practices, PWA category)
// Runs Lighthouse v12 (perf/a11y/best-practices) + v11 (PWA category)
// Usage: node audit-lighthouse.mjs http://localhost:4173

import { spawn } from 'node:child_process';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveReportsDir, readAnchor } from './create-reports-directory.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const anchor = readAnchor(); // ai_skill_anchors/pwa.json — source of truth for project paths
const appDir = path.resolve(anchor._projectRoot, anchor.app_dir);
const reportsDir = resolveReportsDir(); // from ai_skill_anchors/pwa.json (reports_root)

const url = process.argv[2] || 'http://localhost:4173';

const runLighthouse = (command, args, outputPath) => {
  return new Promise((resolve) => {
    console.log(`Running: ${command} ${args.join(' ')}`);
    const proc = spawn(command, args, {
      cwd: appDir,
      stdio: 'inherit',
    });
    proc.on('close', (code) => {
      if (code === 0) {
        console.log(`✓ Lighthouse audit saved to ${outputPath}`);
        resolve(true);
      } else {
        console.error(`✗ Lighthouse exited with code ${code}`);
        resolve(false);
      }
    });
  });
};

const main = async () => {
  try {
    await fs.mkdir(reportsDir, { recursive: true });

    // Run Lighthouse v12 for perf/a11y/best-practices
    const lighthouse1Pass = await runLighthouse('npx', [
      'lighthouse',
      url,
      '--only-categories=performance,accessibility,best-practices',
      '--output=json',
      '--output=html',
      '--output-path=' + path.join(reportsDir, 'lighthouse'),
      // --ignore-certificate-errors: bypass the self-signed-cert interstitial when the target is an
      // HTTPS dev server (e.g. https://localhost:3000). Harmless for http/valid-cert targets.
      '--chrome-flags="--headless=new --ignore-certificate-errors"',
      '--no-enable-error-reporting',
      '--quiet',
    ], path.join(reportsDir, 'lighthouse.report.{json,html}'));

    // Run Lighthouse v11 for PWA category (v12 removed PWA category)
    const lighthouse2Pass = await runLighthouse('npx', [
      '-y',
      'lighthouse@11',
      url,
      '--only-categories=pwa',
      '--output=json',
      '--output=html',
      '--output-path=' + path.join(reportsDir, 'lighthouse-pwa'),
      // --ignore-certificate-errors: bypass the self-signed-cert interstitial when the target is an
      // HTTPS dev server (e.g. https://localhost:3000). Harmless for http/valid-cert targets.
      '--chrome-flags="--headless=new --ignore-certificate-errors"',
      '--no-enable-error-reporting',
      '--quiet',
    ], path.join(reportsDir, 'lighthouse-pwa.report.{json,html}'));

    if (!lighthouse1Pass || !lighthouse2Pass) {
      console.error('Some Lighthouse audits failed');
      process.exit(1);
    }

    console.log('All Lighthouse audits passed');
    process.exit(0);
  } catch (err) {
    console.error('Lighthouse audit failed:', err);
    process.exit(1);
  }
};

main();
