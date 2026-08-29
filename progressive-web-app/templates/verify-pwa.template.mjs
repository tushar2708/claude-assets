#!/usr/bin/env node
// scripts/verify-pwa/verify-pwa.mjs
// Comprehensive app verification orchestrator
// Runs: responsive design (L1) + PWA checks (L1/L2) on both dev and preview servers
// Usage: node scripts/verify-pwa/verify-pwa.mjs

import { spawn } from 'node:child_process';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer as createViteServer } from 'vite';
import http from 'node:http';
import { createReadStream } from 'node:fs';
import { resolveReportsDir, readAnchor } from './create-reports-directory.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const anchor = readAnchor(); // ai_skill_anchors/pwa.json — the source of truth for all project paths
const appDir = path.resolve(anchor._projectRoot, anchor.app_dir);
const reportsDir = resolveReportsDir(); // reports location from ai_skill_anchors/pwa.json

let devServer = null;
let previewServer = null;

const log = (msg) => console.log(`[ORCHESTRATOR] ${msg}`);
const error = (msg) => console.error(`[ERROR] ${msg}`);

// Cleanup on exit
const cleanup = async () => {
  if (devServer) {
    log('Stopping dev server...');
    await devServer.close();
  }
  if (previewServer) {
    log('Stopping preview server...');
    await previewServer.close();
  }
};

process.on('exit', cleanup);
process.on('SIGINT', () => {
  cleanup().then(() => process.exit(1));
});

// Wait for server to be ready using fetch
const waitForServer = async (url, timeout = 30000) => {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      if (response.ok || response.status === 404) {
        log(`Server ready: ${url}`);
        return true;
      }
    } catch {
      // Server not ready, retry
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  error(`Server ${url} did not start within ${timeout}ms`);
  return false;
};

// Run audit script. When `url` is falsy (no external target), the URL arg is omitted
// so each child script falls back to its OWN local default (responsive → :3000,
// pwa/lighthouse → :4173). When `url` is set, all children run against that single URL.
const runAuditScript = (script, url) => {
  return new Promise((resolve) => {
    const args = [path.resolve(__dirname, script)];
    if (url) args.push(url);
    const proc = spawn('node', args, {
      cwd: appDir,
      stdio: 'inherit',
    });
    proc.on('close', (code) => {
      resolve(code === 0);
    });
  });
};

const main = async () => {
  // Optional external target (e.g. production URL) passed as argv[2]. When present,
  // skip the local build + preview and run ALL audits against this single URL. When
  // absent (local mode), build + serve the :4173 preview for the pwa/lighthouse layers
  // and let each child use its own local default (responsive → :3000, pwa/lighthouse → :4173).
  const targetUrl = process.argv[2];

  log('Starting app verification...');

  try {
    if (targetUrl) {
      log(`Auditing external target: ${targetUrl} (skipping local build + preview)`);
    } else {
      // 1. Build
      log('Building app...');
      const { build } = await import('vite');
      await build({
        root: appDir,
        command: 'build',
      });
      log('Build complete');

      // 2. Start preview server (serve dist folder on port 4173)
      log('Starting preview server on http://localhost:4173...');
      const distDir = path.resolve(appDir, 'dist');
      previewServer = http.createServer(async (req, res) => {
        try {
          let filePath = path.join(distDir, req.url === '/' ? 'index.html' : req.url);
          const stat = await fs.stat(filePath);
          if (stat.isDirectory()) filePath = path.join(filePath, 'index.html');
          const content = await fs.readFile(filePath);
          const ext = path.extname(filePath);
          const mimeTypes = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
          res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
          res.end(content);
        } catch {
          res.writeHead(404);
          res.end('Not found');
        }
      });
      previewServer.listen(4173, () => {
        log('Preview server ready');
      });
      const previewReady = await waitForServer('http://localhost:4173');
      if (!previewReady) throw new Error('Preview server failed to start');
    }

    // 3. Run responsive audit on preview server
    log('');
    log('═══════════════════════════════════════════════');
    log('LAYER 1: Responsive Design Audit');
    log('═══════════════════════════════════════════════');
    const responsivePass = await runAuditScript('audit-responsive.mjs', targetUrl);
    if (!responsivePass) error('Responsive audit failed');

    // 4. Run PWA audit on preview server (CDP installability checks)
    log('');
    log('═══════════════════════════════════════════════');
    log('LAYER 2: PWA Installability & Offline Audit');
    log('═══════════════════════════════════════════════');
    const pwaPass = await runAuditScript('audit-pwa.mjs', targetUrl);
    if (!pwaPass) error('PWA audit failed');

    // 5. Run Lighthouse audits on preview server (quality gates) — uses skill tool
    log('');
    log('═══════════════════════════════════════════════');
    log('LAYER 2: PWA Quality Audit (Lighthouse)');
    log('═══════════════════════════════════════════════');
    const lighthousePass = await runAuditScript('audit-lighthouse.mjs', targetUrl);
    if (!lighthousePass) error('Lighthouse audit failed');

    // 6. Generate unified report
    log('Generating unified report...');
    await fs.mkdir(reportsDir, { recursive: true });

    const responsiveResult = JSON.parse(
      await fs.readFile(path.resolve(reportsDir, 'responsive-audit.json'), 'utf8').catch(() => '{}')
    );
    const pwaResult = JSON.parse(
      await fs.readFile(path.resolve(reportsDir, 'pwa-checks.json'), 'utf8').catch(() => '{}')
    );

    const unified = {
      timestamp: new Date().toISOString(),
      suites: {
        responsive: responsiveResult,
        pwa: pwaResult,
      },
      summary: {
        responsivePass,
        pwaPass,
        allPass: responsivePass && pwaPass,
      },
    };

    await fs.writeFile(
      path.resolve(reportsDir, 'verify-app-report.json'),
      JSON.stringify(unified, null, 2)
    );

    log('Report saved to: ' + path.resolve(reportsDir, 'verify-app-report.json'));

    // 7. Generate the final deliverable (PWA_REPORT.md + PWA_REPORT.html) from the JSON outputs.
    //    ALWAYS runs (pass or fail) so this single orchestrator run never leaves partial output.
    log('Generating PWA_REPORT.html (final deliverable)...');
    await import('./generate-reports.mjs');

    if (!responsivePass || !pwaPass || !lighthousePass) {
      error('Some audits failed. See reports for details.');
      process.exit(1);
    }

    log('All audits passed!');
    process.exit(0);
  } catch (err) {
    error(err.message);
    process.exit(1);
  }
};

main();
