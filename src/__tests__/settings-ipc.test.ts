import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock electron before imports
vi.mock('electron', () => ({
  ipcMain: {
    handle: vi.fn(),
  },
}));

// Mock store utils
const mockStore = {
  get: vi.fn(),
  set: vi.fn(),
  delete: vi.fn(),
  clear: vi.fn(),
  store: {},
};

const mockRendererState = new Map<string, string>();

vi.mock('../main/utils/store', () => ({
  getStore: () => mockStore,
  getRendererState: (key: string) => mockRendererState.get(key),
  setRendererState: (key: string, value: string) => mockRendererState.set(key, value),
  removeRendererState: (key: string) => mockRendererState.delete(key),
}));

// Mock bridge
const mockBridge = { restart: vi.fn() };
vi.mock('../main/python/bridge', () => ({
  getPythonBridge: () => mockBridge,
}));

import { ipcMain } from 'electron';
import { registerSettingsHandlers } from '../main/ipc/settings';

// Helper to get a registered IPC handler by channel name
function getHandler(channel: string) {
  const calls = (ipcMain.handle as ReturnType<typeof vi.fn>).mock.calls;
  const match = calls.find((call: unknown[]) => call[0] === channel);
  if (!match) throw new Error(`No handler registered for channel "${channel}"`);
  return match[1]; // The handler function
}

describe('Settings IPC Handlers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockRendererState.clear();
    mockStore.store = {};
    (ipcMain.handle as ReturnType<typeof vi.fn>).mockClear();
    registerSettingsHandlers();
  });

  describe('settings:get', () => {
    it('returns the value from store', async () => {
      mockStore.get.mockReturnValue('test-value');
      const handler = getHandler('settings:get');
      const result = await handler({}, 'someKey');
      expect(mockStore.get).toHaveBeenCalledWith('someKey');
      expect(result).toBe('test-value');
    });
  });

  describe('settings:set', () => {
    it('sets a simple setting without restarting bridge', async () => {
      const handler = getHandler('settings:set');
      const result = await handler({}, 'ui.fontSize', 14);
      expect(mockStore.set).toHaveBeenCalledWith('ui.fontSize', 14);
      expect(mockBridge.restart).not.toHaveBeenCalled();
      expect(result).toEqual({ success: true });
    });

    it('restarts Python bridge when LLM config changes', async () => {
      mockStore.get.mockReturnValue('old-value');
      const handler = getHandler('settings:set');
      await handler({}, 'llm.mode', 'api');
      expect(mockStore.set).toHaveBeenCalledWith('llm.mode', 'api');
      expect(mockBridge.restart).toHaveBeenCalled();
    });

    it('does NOT restart bridge when LLM value is unchanged', async () => {
      mockStore.get.mockReturnValue('local');
      const handler = getHandler('settings:set');
      await handler({}, 'llm.mode', 'local');
      expect(mockStore.set).toHaveBeenCalledWith('llm.mode', 'local');
      expect(mockBridge.restart).not.toHaveBeenCalled();
    });

    it('restarts bridge when app.outputDir changes', async () => {
      mockStore.get.mockReturnValue('/old/path');
      const handler = getHandler('settings:set');
      await handler({}, 'app.outputDir', '/new/path');
      expect(mockBridge.restart).toHaveBeenCalled();
    });

    it('restarts bridge when app.language changes', async () => {
      mockStore.get.mockReturnValue('es');
      const handler = getHandler('settings:set');
      await handler({}, 'app.language', 'en');
      expect(mockBridge.restart).toHaveBeenCalled();
    });

    it('returns error object on exception', async () => {
      mockStore.get.mockImplementation(() => { throw new Error('Store failure'); });
      const handler = getHandler('settings:set');
      // For llm.* path, get is called first
      const result = await handler({}, 'llm.mode', 'api');
      expect(result).toEqual({ success: false, error: 'Store failure' });
    });
  });

  describe('settings:get-all', () => {
    it('returns entire store', async () => {
      mockStore.store = { llm: { mode: 'local' }, app: { language: 'es' } };
      const handler = getHandler('settings:get-all');
      const result = await handler({});
      expect(result).toEqual({ llm: { mode: 'local' }, app: { language: 'es' } });
    });
  });

  describe('settings:reset', () => {
    it('clears the store', async () => {
      const handler = getHandler('settings:reset');
      const result = await handler({});
      expect(mockStore.clear).toHaveBeenCalled();
      expect(result).toEqual({ success: true });
    });
  });

  describe('settings:delete', () => {
    it('deletes a specific key', async () => {
      const handler = getHandler('settings:delete');
      const result = await handler({}, 'someKey');
      expect(mockStore.delete).toHaveBeenCalledWith('someKey');
      expect(result).toEqual({ success: true });
    });
  });

  describe('store:set-item / store:get-item / store:remove-item', () => {
    it('persists renderer state via set/get', async () => {
      const setHandler = getHandler('store:set-item');
      const getHandler_ = getHandler('store:get-item');

      await setHandler({}, 'zustand-key', '{"count":1}');
      const result = await getHandler_({}, 'zustand-key');
      expect(result).toBe('{"count":1}');
    });

    it('removes renderer state', async () => {
      const setHandler = getHandler('store:set-item');
      const removeHandler = getHandler('store:remove-item');
      const getHandler_ = getHandler('store:get-item');

      await setHandler({}, 'key1', 'value1');
      await removeHandler({}, 'key1');
      const result = await getHandler_({}, 'key1');
      expect(result).toBeUndefined();
    });
  });
});
