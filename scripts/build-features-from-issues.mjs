#!/usr/bin/env node
// Generates frontend/lib/features.ts from GitHub issues labeled `feature` with status labels
// Status labels are: live, beta, coming, planned (as plain labels or as form value in issue body)

const OWNER_REPO = process.env.GITHUB_REPOSITORY || 'XDM-ZSBW/JobMatch.Zip';
const [owner, repo] = OWNER_REPO.split('/');
const token = process.env.GITHUB_TOKEN;
if (!token) {
  console.error('GITHUB_TOKEN not set');
  process.exit(1);
}

const api = async (path, init = {}) => {
  const res = await fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'User-Agent': 'features-codegen',
      ...(init.headers || {})
    }
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
};

// Fetch open issues with label `feature`
const issues = await api(`/repos/${owner}/${repo}/issues?state=open&labels=feature&per_page=100`);

const STATUS_SET = new Set(['live','beta','coming','planned']);
const features = [];
for (const it of issues) {
  // derive label and status
  const label = it.title.trim();
  let status = null;
  for (const l of it.labels) {
    const name = (typeof l === 'string' ? l : l.name).toLowerCase();
    if (STATUS_SET.has(name)) { status = name; break; }
  }
  if (!status) {
    // try to parse from issue body (from form)
    const m = it.body && it.body.match(/status:\s*(live|beta|coming|planned)/i);
    if (m) status = m[1].toLowerCase();
  }
  if (!status) continue; // skip until status is present
  features.push({ label, status });
}

// Fallback: if no issues present, keep existing defaults (do nothing)
if (features.length === 0) {
  console.log('No feature issues with status found; skipping write');
  process.exit(0);
}

// Build TypeScript file
const ts = `export type FeatureStatus = 'live' | 'beta' | 'coming' | 'planned';\nexport type Feature = { label: string; status: FeatureStatus };\n\nexport const FEATURES: Feature[] = ${JSON.stringify(features, null, 2)} as const;\n\nexport const LEGEND = [\n  { status: 'live' as FeatureStatus, label: 'Live', icon: '✅', color: 'text-green-600' },\n  { status: 'beta' as FeatureStatus, label: 'Beta', icon: '🧪', color: 'text-amber-500' },\n  { status: 'coming' as FeatureStatus, label: 'Coming', icon: '🕒', color: 'text-gray-500' },\n  { status: 'planned' as FeatureStatus, label: 'Planned', icon: '◌', color: 'text-gray-500' },\n];\n`;

import { writeFile } from 'node:fs/promises';
await writeFile('frontend/lib/features.ts', ts, 'utf8');
console.log('Wrote frontend/lib/features.ts from issues');