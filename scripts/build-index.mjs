#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');
const articlesDir = path.join(rootDir, 'articles');
const indexFile = path.join(rootDir, 'index.json');

function parseFrontMatter(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);
  if (!match) return {};

  const metadata = {};
  let currentKey = null;

  for (const rawLine of match[1].split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;

    const keyMatch = line.match(/^([^:]+):\s*(.*)$/);
    if (keyMatch) {
      const key = keyMatch[1].trim();
      let value = keyMatch[2].trim();

      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      if (value.startsWith('[') && value.endsWith(']')) {
        value = value
          .slice(1, -1)
          .split(',')
          .map(v => v.trim().replace(/^['"]|['"]$/g, ''))
          .filter(Boolean);
      }

      metadata[key] = value;
      currentKey = key;
      continue;
    }

    if (line.startsWith('-') && currentKey) {
      if (!Array.isArray(metadata[currentKey])) {
        metadata[currentKey] = [];
      }
      metadata[currentKey].push(line.slice(1).trim().replace(/^['"]|['"]$/g, ''));
    }
  }

  if (metadata.keywords && typeof metadata.keywords === 'string') {
    metadata.keywords = metadata.keywords
      .split(',')
      .map(item => item.trim())
      .filter(Boolean);
  }

  return metadata;
}

function extractMarkdownContent(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);
  if (match) {
    return content.slice(match[0].length).trim();
  }
  return content.trim();
}

function validateMetadata(metadata, filename) {
  const required = ['track', 'name', 'order'];

  for (const key of required) {
    if (!metadata[key]) {
      throw new Error(`${filename}: missing required field "${key}"`);
    }
  }

  const order = Number(metadata.order);
  if (!Number.isInteger(order)) {
    throw new Error(`${filename}: "order" must be an integer`);
  }
}

async function buildIndex() {
  const files = await fs.readdir(articlesDir);

  const markdownFiles = files
    .filter(file => file.endsWith('.md'))
    .sort();

  const entries = [];

  for (const file of markdownFiles) {
    const fullPath = path.join(articlesDir, file);
    const content = await fs.readFile(fullPath, 'utf8');

    const metadata = parseFrontMatter(content);
    validateMetadata(metadata, file);

    const id = file.replace(/\.md$/, '');
    const markdownContent = extractMarkdownContent(content);

    entries.push({
      '@id': id,
      track: metadata.track,
      discipline: metadata.discipline || 'General',
      order: Number(metadata.order),
      name: metadata.name,
      description: metadata.description || '',
      keywords: Array.isArray(metadata.keywords) ? metadata.keywords : [],
      text: `articles/${file}`,
      markdownContent: markdownContent,
      encodingFormat: 'text/markdown'
    });
  }

  entries.sort((a, b) => {
    if (a.track !== b.track) return a.track.localeCompare(b.track);
    return a.order - b.order;
  });

  await fs.writeFile(indexFile, JSON.stringify(entries, null, 2) + '\n');
  console.log(`Generated ${indexFile} with ${entries.length} module(s)`);
}

buildIndex().catch(err => {
  console.error(err.message);
  process.exit(1);
});
