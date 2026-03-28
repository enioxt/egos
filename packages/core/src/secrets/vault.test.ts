/**
 * Tests for secrets vault implementations
 * EGOS-004.1 acceptance criteria validation
 */

import {
  EnvSecretStore,
  createSecretStore,
  getSecretStore,
  resetSecretStore
} from './vault';

describe('EnvSecretStore', () => {
  let store: EnvSecretStore;

  beforeEach(() => {
    store = new EnvSecretStore();
    process.env.TEST_SECRET = 'test-value-123';
    process.env.OPENAI_API_KEY = 'sk-test-key';
  });

  afterEach(() => {
    delete process.env.TEST_SECRET;
    delete process.env.OPENAI_API_KEY;
  });

  test('should get secret from environment variable', async () => {
    const value = await store.get('TEST_SECRET');
    expect(value).toBe('test-value-123');
  });

  test('should return undefined for missing secret', async () => {
    const value = await store.get('NONEXISTENT_SECRET');
    expect(value).toBeUndefined();
  });

  test('should list available secrets', async () => {
    const keys = await store.list();
    expect(keys).toContain('OPENAI_API_KEY');
    expect(keys).not.toContain('NONEXISTENT_KEY');
  });

  test('should check secret existence', async () => {
    const exists = await store.exists('OPENAI_API_KEY');
    expect(exists).toBe(true);

    const missing = await store.exists('MISSING_SECRET');
    expect(missing).toBe(false);
  });

  test('should throw on set operation (read-only)', async () => {
    await expect(store.set('KEY', 'value')).rejects.toThrow(
      'read-only'
    );
  });

  test('should throw on delete operation (read-only)', async () => {
    await expect(store.delete('KEY')).rejects.toThrow(
      'read-only'
    );
  });
});

describe('createSecretStore', () => {
  beforeEach(() => {
    resetSecretStore();
  });

  test('should create EnvSecretStore by default', () => {
    const store = createSecretStore('env');
    expect(store).toBeInstanceOf(EnvSecretStore);
  });

  test('should throw on vault without config', () => {
    delete process.env.VAULT_ADDR;
    delete process.env.VAULT_TOKEN;
    expect(() => createSecretStore('vault')).toThrow(
      'VAULT_ADDR or VAULT_TOKEN not set'
    );
  });
});

describe('getSecretStore singleton', () => {
  beforeEach(() => {
    resetSecretStore();
  });

  test('should return same instance on multiple calls', () => {
    const store1 = getSecretStore();
    const store2 = getSecretStore();
    expect(store1).toBe(store2);
  });

  test('should support reset for testing', () => {
    const store1 = getSecretStore();
    resetSecretStore();
    const store2 = getSecretStore();
    expect(store1).not.toBe(store2);
  });
});
