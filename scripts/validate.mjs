#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const INDEX_FILE = path.join(ROOT, 'index.json');

/**
 * JSON Schema validator for index.json
 */
const SCHEMA = {
  type: 'array',
  items: {
    type: 'object',
    required: ['@id', 'track', 'name', 'order', 'text'],
    properties: {
      '@id': { type: 'string' },
      track: { type: 'string' },
      discipline: { type: 'string' },
      order: { type: 'number', minimum: 0 },
      name: { type: 'string' },
      description: { type: 'string' },
      keywords: {
        type: 'array',
        items: { type: 'string' },
      },
      text: { type: 'string' },
      encodingFormat: { type: 'string' },
    },
  },
};

/**
 * Validate a value against a simple schema.
 */
function validateAgainstSchema(data, schema, path = '$') {
  const errors = [];

  if (schema.type === 'array') {
    if (!Array.isArray(data)) {
      errors.push(`${path} must be an array`);
      return errors;
    }

    if (schema.items) {
      data.forEach((item, index) => {
        const itemErrors = validateAgainstSchema(item, schema.items, `${path}[${index}]`);
        errors.push(...itemErrors);
      });
    }
  } else if (schema.type === 'object') {
    if (typeof data !== 'object' || data === null) {
      errors.push(`${path} must be an object`);
      return errors;
    }

    // Check required fields
    if (schema.required) {
      for (const field of schema.required) {
        if (!(field in data)) {
          errors.push(`${path}.${field} is required`);
        }
      }
    }

    // Validate each property
    if (schema.properties) {
      for (const [key, propSchema] of Object.entries(schema.properties)) {
        if (key in data) {
          const propErrors = validateAgainstSchema(data[key], propSchema, `${path}.${key}`);
          errors.push(...propErrors);
        }
      }
    }
  } else if (schema.type === 'string') {
    if (typeof data !== 'string') {
      errors.push(`${path} must be a string`);
    }
  } else if (schema.type === 'number') {
    if (typeof data !== 'number') {
      errors.push(`${path} must be a number`);
    }
    if (schema.minimum !== undefined && data < schema.minimum) {
      errors.push(`${path} must be >= ${schema.minimum}`);
    }
  }

  return errors;
}

/**
 * Main validation function.
 */
async function validate() {
  console.log(`📋 Validating: ${INDEX_FILE}`);

  let rawData;
  try {
    const content = await fs.readFile(INDEX_FILE, 'utf-8');
    rawData = JSON.parse(content);
  } catch (err) {
    console.error(`❌ Failed to read/parse index.json: ${err.message}`);
    process.exit(1);
  }

  const schemaErrors = validateAgainstSchema(rawData, SCHEMA);

  if (schemaErrors.length > 0) {
    console.error('❌ Validation failed:');
    schemaErrors.forEach(e => console.error(`   - ${e}`));
    process.exit(1);
  }

  // Additional checks
  const ids = new Set();
  let hasIssues = false;

  for (let i = 0; i < rawData.length; i++) {
    const entry = rawData[i];

    // Check for duplicate @id
    if (ids.has(entry['@id'])) {
      console.error(`❌ Duplicate @id: "${entry['@id']}"`);
      hasIssues = true;
    }
    ids.add(entry['@id']);

    // Check that text file exists
    const textPath = path.join(ROOT, entry.text);
    try {
      await fs.access(textPath);
    } catch {
      console.error(`❌ Missing file: ${entry.text} (referenced by @id: ${entry['@id']})`);
      hasIssues = true;
    }
  }

  if (hasIssues) {
    process.exit(1);
  }

  console.log(`✅ Valid index.json`);
  console.log(`📊 Total modules: ${rawData.length}`);
  console.log(`✅ All referenced files exist`);
}

validate().catch(err => {
  console.error('❌ Unexpected error:', err);
  process.exit(1);
});
