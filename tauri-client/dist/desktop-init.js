/**
 * Desktop-specific initialization for Tauri client
 * This script is injected into the app when running in desktop mode
 */

document.addEventListener("DOMContentLoaded", function() {
  // Wait for TauriBridge to be available
  const initDesktop = () => {
    if (!window.TauriBridge || !window.TauriBridge.isTauri()) {
      console.log("Running in browser mode");
      return;
    }

    console.log("Initializing desktop enhancements...");

    // Add platform class
    window.TauriBridge.system.getPlatform().then(function(platform) {
      const p = platform.toLowerCase();
      if (p.includes("mac") || p.includes("darwin")) {
        document.body.classList.add("platform-macos");
      } else if (p.includes("win")) {
        document.body.classList.add("platform-windows");
      } else {
        document.body.classList.add("platform-linux");
      }
    });

    // Wait for ui to be available
    const waitForUI = setInterval(() => {
      if (typeof ui !== "undefined" && typeof appState !== "undefined") {
        clearInterval(waitForUI);
        enhanceUI();
      }
    }, 100);

    function enhanceUI() {
      // Override export functions to use native dialogs
      if (ui.exportAllData) {
        const originalExportAllData = ui.exportAllData.bind(ui);
        ui.exportAllData = async function() {
          const exportData = appState.exportAllData();
          const filename = "rappid-full-backup-" + new Date().toISOString().replace(/:/g, "-") + ".json";
          const result = await window.TauriBridge.fileOps.exportData(exportData, filename);
          if (result.success && !result.cancelled) {
            this.showNotification("Backup saved!", "success");
          } else if (!result.cancelled) {
            originalExportAllData();
          }
        };
      }

      if (ui.exportSettings) {
        const originalExportSettings = ui.exportSettings.bind(ui);
        ui.exportSettings = async function() {
          const settingsData = appState.exportSettings ? appState.exportSettings() : { settings: appState.settings, endpoints: appState.endpoints };
          const filename = "rappid-settings-" + new Date().toISOString().replace(/:/g, "-") + ".json";
          const result = await window.TauriBridge.fileOps.exportData(settingsData, filename);
          if (result.success && !result.cancelled) {
            this.showNotification("Settings exported!", "success");
          } else if (!result.cancelled) {
            originalExportSettings();
          }
        };
      }

      if (ui.exportCurrentChat) {
        const originalExportChat = ui.exportCurrentChat.bind(ui);
        ui.exportCurrentChat = async function() {
          if (!appState.currentChatId) return;
          const chat = appState.chats[appState.currentUser.id][appState.currentChatId];
          const conversation = chat.messages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          }));
          const endpoint = appState.getActiveEndpoint();
          const exportData = {
            conversation: conversation,
            guid: endpoint.guid,
            timestamp: new Date().toISOString(),
            appName: "Copilot Agent 365 Desktop",
          };
          const filename = "conversation-" + new Date().toISOString().replace(/:/g, "_") + ".json";
          const result = await window.TauriBridge.fileOps.exportData(exportData, filename);
          if (result.success && !result.cancelled) {
            this.showNotification("Conversation exported!", "success");
          } else if (!result.cancelled) {
            originalExportChat();
          }
        };
      }

      // Desktop notification for new messages when window is not focused
      if (ui.showNotification) {
        const originalShowNotification = ui.showNotification.bind(ui);
        ui.showNotification = function(message, type) {
          originalShowNotification(message, type);
          if (type === "success" && document.hidden) {
            window.TauriBridge.notifications.show("Copilot Agent 365", message);
          }
        };
      }

      // Update window title with current chat name
      const updateWindowTitle = () => {
        if (appState.currentChatId && appState.currentUser) {
          const chat = appState.chats[appState.currentUser.id][appState.currentChatId];
          if (chat) {
            window.TauriBridge.window.setTitle(chat.title + " - Copilot Agent 365");
          }
        }
      };

      // Override loadChat to update window title
      if (ui.loadChat) {
        const originalLoadChat = ui.loadChat.bind(ui);
        ui.loadChat = function(chatId) {
          originalLoadChat(chatId);
          setTimeout(updateWindowTitle, 100);
        };
      }

      console.log("Desktop UI enhancements applied");
    }

    // Keyboard shortcuts
    document.addEventListener("keydown", function(e) {
      // Only trigger if not in an input field
      const isInputFocused = document.activeElement.tagName === "INPUT" ||
                            document.activeElement.tagName === "TEXTAREA" ||
                            document.activeElement.isContentEditable;

      // Cmd/Ctrl + , for settings
      if ((e.metaKey || e.ctrlKey) && e.key === ",") {
        e.preventDefault();
        if (typeof ui !== "undefined" && ui.openSettings) {
          ui.openSettings();
        }
      }

      // Cmd/Ctrl + N for new chat
      if ((e.metaKey || e.ctrlKey) && e.key === "n") {
        e.preventDefault();
        if (typeof ui !== "undefined" && ui.createNewChat) {
          ui.createNewChat();
        }
      }

      // Cmd/Ctrl + E for export
      if ((e.metaKey || e.ctrlKey) && e.key === "e" && !isInputFocused) {
        e.preventDefault();
        if (typeof ui !== "undefined" && ui.exportAllData) {
          ui.exportAllData();
        }
      }

      // Cmd/Ctrl + Shift + E for export current chat
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "E" && !isInputFocused) {
        e.preventDefault();
        if (typeof ui !== "undefined" && ui.exportCurrentChat) {
          ui.exportCurrentChat();
        }
      }

      // Cmd/Ctrl + D for dark mode toggle
      if ((e.metaKey || e.ctrlKey) && e.key === "d" && !isInputFocused) {
        e.preventDefault();
        if (typeof ui !== "undefined" && ui.toggleDarkMode) {
          ui.toggleDarkMode();
        }
      }

      // Cmd/Ctrl + / for help
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        // Show keyboard shortcuts help
        showKeyboardShortcutsHelp();
      }
    });

    // Create keyboard shortcuts help modal
    function showKeyboardShortcutsHelp() {
      const existingModal = document.getElementById("keyboard-shortcuts-modal");
      if (existingModal) {
        existingModal.remove();
        return;
      }

      const isMac = navigator.platform.toLowerCase().includes("mac");
      const modKey = isMac ? "⌘" : "Ctrl";

      const modal = document.createElement("div");
      modal.id = "keyboard-shortcuts-modal";
      modal.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      `;

      modal.innerHTML = `
        <div style="
          background: var(--gray-10);
          border-radius: 16px;
          padding: 24px;
          max-width: 400px;
          box-shadow: var(--shadow-large);
        ">
          <h2 style="margin: 0 0 16px 0; font-size: 18px; color: var(--gray-100);">
            <i class="fas fa-keyboard" style="margin-right: 8px;"></i>
            Keyboard Shortcuts
          </h2>
          <div style="display: grid; gap: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">New Chat</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + N</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">Settings</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + ,</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">Export All Data</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + E</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">Export Current Chat</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + ⇧ + E</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">Toggle Dark Mode</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + D</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: var(--gray-80);">Show Shortcuts</span>
              <kbd style="background: var(--gray-30); padding: 4px 8px; border-radius: 4px; font-family: monospace;">${modKey} + /</kbd>
            </div>
          </div>
          <button onclick="this.closest('#keyboard-shortcuts-modal').remove()" style="
            margin-top: 20px;
            width: 100%;
            padding: 10px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
          ">Close</button>
        </div>
      `;

      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.remove();
      });

      document.body.appendChild(modal);
    }

    // Window focus/blur handling
    window.addEventListener("focus", () => {
      document.body.classList.remove("window-blur");
    });

    window.addEventListener("blur", () => {
      document.body.classList.add("window-blur");
    });

    // Create drag-drop overlay for file imports
    const dragDropOverlay = document.createElement("div");
    dragDropOverlay.className = "drag-drop-overlay";
    dragDropOverlay.innerHTML = `
      <div class="drag-drop-overlay-content">
        <i class="fas fa-file-import"></i>
        <h3>Drop to Import</h3>
        <p>Release to import your backup file</p>
      </div>
    `;
    document.body.appendChild(dragDropOverlay);

    let dragCounter = 0;

    document.addEventListener("dragenter", (e) => {
      e.preventDefault();
      dragCounter++;
      if (e.dataTransfer.types.includes("Files")) {
        dragDropOverlay.classList.add("active");
      }
    });

    document.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter === 0) {
        dragDropOverlay.classList.remove("active");
      }
    });

    document.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    document.addEventListener("drop", async (e) => {
      e.preventDefault();
      dragCounter = 0;
      dragDropOverlay.classList.remove("active");

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const file = files[0];
        if (file.type === "application/json" || file.name.endsWith(".json")) {
          const reader = new FileReader();
          reader.onload = async (event) => {
            try {
              const data = JSON.parse(event.target.result);
              // Try to import the data
              if (typeof ui !== "undefined" && typeof appState !== "undefined") {
                if (data.users || data.chats) {
                  appState.importAllData(data);
                  ui.showNotification("Data imported successfully!", "success");
                  if (ui.loadUserChats) ui.loadUserChats("active");
                } else if (data.endpoints || data.settings) {
                  if (appState.importSettings) {
                    appState.importSettings(data);
                  }
                  ui.showNotification("Settings imported successfully!", "success");
                }
              }
            } catch (err) {
              console.error("Import error:", err);
              if (typeof ui !== "undefined") {
                ui.showNotification("Failed to import file: " + err.message, "error");
              }
            }
          };
          reader.readAsText(file);
        }
      }
    });

    console.log("Copilot Agent 365 Desktop initialized");
  };

  // Initialize with a small delay to ensure TauriBridge is loaded
  setTimeout(initDesktop, 100);
});
