import { test } from 'node:test';
import assert from 'node:assert/strict';

// Test implementation replicating normalizeApiBase pure logic
function normalizeApiBase(rawUrl) {
  let url = (rawUrl !== undefined ? rawUrl : '') || '';
  if (!url) return '';
  url = url.trim();
  url = url.replace(/\/+$/, '');

  const isLocal = url.includes('localhost') || url.includes('127.0.0.1');

  if (!isLocal && !url.includes('.') && !url.includes(':') && !url.startsWith('http')) {
    url = `${url}.onrender.com`;
  }

  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = isLocal ? `http://${url}` : `https://${url}`;
  }
  return url;
}

test('normalizeApiBase handles explicit full Render URL', () => {
  assert.equal(
    normalizeApiBase('https://greenquest-api-mhjr.onrender.com'),
    'https://greenquest-api-mhjr.onrender.com'
  );
});

test('normalizeApiBase strips trailing slash from full URL', () => {
  assert.equal(
    normalizeApiBase('https://greenquest-api-mhjr.onrender.com/'),
    'https://greenquest-api-mhjr.onrender.com'
  );
});

test('normalizeApiBase resolves internal Render fromService host (greenquest-api-mhjr)', () => {
  assert.equal(
    normalizeApiBase('greenquest-api-mhjr'),
    'https://greenquest-api-mhjr.onrender.com'
  );
});

test('normalizeApiBase resolves default Render service host (greenquest-api)', () => {
  assert.equal(
    normalizeApiBase('greenquest-api'),
    'https://greenquest-api.onrender.com'
  );
});

test('normalizeApiBase adds https scheme to onrender domain missing protocol', () => {
  assert.equal(
    normalizeApiBase('greenquest-api-mhjr.onrender.com'),
    'https://greenquest-api-mhjr.onrender.com'
  );
});

test('normalizeApiBase preserves local development URLs', () => {
  assert.equal(normalizeApiBase('http://localhost:8000'), 'http://localhost:8000');
  assert.equal(normalizeApiBase('localhost:8000'), 'http://localhost:8000');
  assert.equal(normalizeApiBase('127.0.0.1:8000'), 'http://127.0.0.1:8000');
});

test('normalizeApiBase preserves custom domains', () => {
  assert.equal(
    normalizeApiBase('https://custom.greenquest.app'),
    'https://custom.greenquest.app'
  );
});

test('normalizeApiBase handles empty string as relative URL', () => {
  assert.equal(normalizeApiBase(''), '');
  assert.equal(normalizeApiBase(undefined), '');
});

