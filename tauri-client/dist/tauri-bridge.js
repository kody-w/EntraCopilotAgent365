/**
 * Tauri Bridge - Native Desktop Integration Layer
 *
 * This module provides a seamless integration between the web application
 * and Tauri's native capabilities when running as a desktop app.
 */

// Check if we're running in Tauri
const isTauri = () => {
  return window.__TAURI__ !== undefined;
};

// Tauri API imports (will be available when running in Tauri)
let invoke, dialog, fs, notification, clipboard, os, store;

// Initialize Tauri APIs when available
async function initTauriAPIs() {
  if (!isTauri()) {
    console.log('Running in browser mode - Tauri APIs not available');
    return false;
  }

  try {
    invoke = window.__TAURI__.core.invoke;

    // Import dialog plugin
    dialog = {
      open: window.__TAURI__.dialog?.open,
      save: window.__TAURI__.dialog?.save,
      message: window.__TAURI__.dialog?.message,
      ask: window.__TAURI__.dialog?.ask,
      confirm: window.__TAURI__.dialog?.confirm
    };

    // Import fs plugin
    fs = {
      readFile: window.__TAURI__.fs?.readFile,
      writeFile: window.__TAURI__.fs?.writeFile,
      readDir: window.__TAURI__.fs?.readDir,
      exists: window.__TAURI__.fs?.exists,
      mkdir: window.__TAURI__.fs?.mkdir
    };

    // Import notification plugin
    notification = {
      sendNotification: window.__TAURI__.notification?.sendNotification,
      requestPermission: window.__TAURI__.notification?.requestPermission,
      isPermissionGranted: window.__TAURI__.notification?.isPermissionGranted
    };

    // Import clipboard plugin
    clipboard = {
      readText: window.__TAURI__.clipboardManager?.readText,
      writeText: window.__TAURI__.clipboardManager?.writeText
    };

    // Import os plugin
    os = {
      platform: window.__TAURI__.os?.platform,
      version: window.__TAURI__.os?.version,
      arch: window.__TAURI__.os?.arch,
      type: window.__TAURI__.os?.type
    };

    console.log('Tauri APIs initialized successfully');
    return true;
  } catch (error) {
    console.error('Failed to initialize Tauri APIs:', error);
    return false;
  }
}

// Native Desktop Store - Extends localStorage with native file-backed storage
class TauriStore {
  constructor(filename = 'app-data.json') {
    this.filename = filename;
    this.store = null;
    this.initialized = false;
  }

  async init() {
    if (!isTauri()) {
      console.log('TauriStore: Using localStorage fallback');
      this.initialized = true;
      return;
    }

    try {
      // Use Tauri's store plugin if available
      if (window.__TAURI__?.store) {
        const { Store } = window.__TAURI__.store;
        this.store = new Store(this.filename);
        await this.store.load();
      }
      this.initialized = true;
    } catch (error) {
      console.warn('TauriStore init failed, using localStorage:', error);
      this.initialized = true;
    }
  }

  async get(key) {
    if (this.store) {
      return await this.store.get(key);
    }
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  }

  async set(key, value) {
    if (this.store) {
      await this.store.set(key, value);
      await this.store.save();
    } else {
      localStorage.setItem(key, JSON.stringify(value));
    }
  }

  async delete(key) {
    if (this.store) {
      await this.store.delete(key);
      await this.store.save();
    } else {
      localStorage.removeItem(key);
    }
  }
}

// Desktop File Operations
const DesktopFileOps = {
  async exportData(data, defaultFilename) {
    if (!isTauri() || !dialog?.save) {
      // Fallback to browser download
      return this.browserDownload(data, defaultFilename);
    }

    try {
      const filePath = await dialog.save({
        defaultPath: defaultFilename,
        filters: [{
          name: 'JSON',
          extensions: ['json']
        }]
      });

      if (filePath) {
        const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        await invoke('export_data', { path: filePath, data: content });
        return { success: true, path: filePath };
      }
      return { success: false, cancelled: true };
    } catch (error) {
      console.error('Export failed:', error);
      return { success: false, error: error.message };
    }
  },

  async importData(fileTypes = ['json']) {
    if (!isTauri() || !dialog?.open) {
      // Fallback to file input
      return this.browserImport();
    }

    try {
      const filePath = await dialog.open({
        multiple: false,
        filters: [{
          name: 'Data Files',
          extensions: fileTypes
        }]
      });

      if (filePath) {
        const content = await invoke('import_data', { path: filePath });
        return { success: true, data: JSON.parse(content) };
      }
      return { success: false, cancelled: true };
    } catch (error) {
      console.error('Import failed:', error);
      return { success: false, error: error.message };
    }
  },

  browserDownload(data, filename) {
    const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    return { success: true };
  },

  browserImport() {
    return new Promise((resolve) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            try {
              const data = JSON.parse(event.target.result);
              resolve({ success: true, data });
            } catch (error) {
              resolve({ success: false, error: 'Invalid JSON' });
            }
          };
          reader.readAsText(file);
        } else {
          resolve({ success: false, cancelled: true });
        }
      };
      input.click();
    });
  }
};

// Desktop Notifications
const DesktopNotifications = {
  async show(title, body, options = {}) {
    if (isTauri() && notification?.sendNotification) {
      try {
        const permission = await notification.isPermissionGranted();
        if (!permission) {
          await notification.requestPermission();
        }
        await notification.sendNotification({ title, body, ...options });
        return true;
      } catch (error) {
        console.warn('Native notification failed:', error);
      }
    }

    // Fallback to browser notification
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body, ...options });
        return true;
      } else if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          new Notification(title, { body, ...options });
          return true;
        }
      }
    }
    return false;
  }
};

// Desktop Clipboard Operations
const DesktopClipboard = {
  async write(text) {
    if (isTauri() && clipboard?.writeText) {
      try {
        await clipboard.writeText(text);
        return true;
      } catch (error) {
        console.warn('Native clipboard write failed:', error);
      }
    }

    // Fallback to browser clipboard
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Clipboard write failed:', error);
      return false;
    }
  },

  async read() {
    if (isTauri() && clipboard?.readText) {
      try {
        return await clipboard.readText();
      } catch (error) {
        console.warn('Native clipboard read failed:', error);
      }
    }

    // Fallback to browser clipboard
    try {
      return await navigator.clipboard.readText();
    } catch (error) {
      console.error('Clipboard read failed:', error);
      return null;
    }
  }
};

// Native HTTP Client - Uses Rust backend for better security
const NativeHttp = {
  async sendChatMessage(endpointUrl, apiKey, userInput, conversationHistory, userGuid) {
    if (isTauri() && invoke) {
      try {
        return await invoke('send_chat_message', {
          endpoint_url: endpointUrl,
          api_key: apiKey || null,
          user_input: userInput,
          conversation_history: conversationHistory,
          user_guid: userGuid || null
        });
      } catch (error) {
        console.warn('Native HTTP failed, falling back to fetch:', error);
      }
    }

    // Fallback to fetch
    const headers = { 'Content-Type': 'application/json' };
    if (apiKey) {
      headers['x-functions-key'] = apiKey;
    }

    const response = await fetch(endpointUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        user_input: userInput,
        conversation_history: conversationHistory,
        user_guid: userGuid
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  async testEndpoint(endpointUrl, apiKey) {
    if (isTauri() && invoke) {
      try {
        return await invoke('test_endpoint', {
          endpoint_url: endpointUrl,
          api_key: apiKey || null
        });
      } catch (error) {
        console.warn('Native test failed:', error);
        return false;
      }
    }

    // Fallback to fetch
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (apiKey) {
        headers['x-functions-key'] = apiKey;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(endpointUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify({ user_input: 'ping', conversation_history: [] }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
};

// System Information
const SystemInfo = {
  async get() {
    if (isTauri() && invoke) {
      try {
        return await invoke('get_system_info');
      } catch (error) {
        console.warn('Failed to get system info:', error);
      }
    }

    return {
      os: navigator.platform,
      userAgent: navigator.userAgent,
      language: navigator.language
    };
  },

  isTauri: isTauri,

  async getPlatform() {
    if (isTauri() && os?.platform) {
      return await os.platform();
    }
    return navigator.platform;
  }
};

// Window Controls (for custom titlebar if needed)
const WindowControls = {
  async minimize() {
    if (isTauri() && window.__TAURI__?.window) {
      const { getCurrentWindow } = window.__TAURI__.window;
      await getCurrentWindow().minimize();
    }
  },

  async maximize() {
    if (isTauri() && window.__TAURI__?.window) {
      const { getCurrentWindow } = window.__TAURI__.window;
      const win = getCurrentWindow();
      if (await win.isMaximized()) {
        await win.unmaximize();
      } else {
        await win.maximize();
      }
    }
  },

  async close() {
    if (isTauri() && window.__TAURI__?.window) {
      const { getCurrentWindow } = window.__TAURI__.window;
      await getCurrentWindow().close();
    } else {
      window.close();
    }
  },

  async setTitle(title) {
    if (isTauri() && window.__TAURI__?.window) {
      const { getCurrentWindow } = window.__TAURI__.window;
      await getCurrentWindow().setTitle(title);
    } else {
      document.title = title;
    }
  }
};

// Initialize on load
let tauriInitialized = false;
const tauriStore = new TauriStore();

document.addEventListener('DOMContentLoaded', async () => {
  tauriInitialized = await initTauriAPIs();
  await tauriStore.init();

  // Add desktop-specific class to body
  if (isTauri()) {
    document.body.classList.add('tauri-desktop');
    console.log('Copilot Agent 365 Desktop - Running in Tauri');
  }
});

// Export for use in main application
window.TauriBridge = {
  isTauri,
  isInitialized: () => tauriInitialized,
  store: tauriStore,
  fileOps: DesktopFileOps,
  notifications: DesktopNotifications,
  clipboard: DesktopClipboard,
  http: NativeHttp,
  system: SystemInfo,
  window: WindowControls
};

console.log('Tauri Bridge loaded - Mode:', isTauri() ? 'Desktop' : 'Browser');
