# Copilot Agent 365 - Desktop Client

A native desktop application built with [Tauri](https://tauri.app/) for the Copilot Agent 365 AI chat assistant.

## Features

- **Native Desktop Experience**: Runs as a native application on Windows, macOS, and Linux
- **Native File Dialogs**: Export and import data using native OS file dialogs
- **Desktop Notifications**: Receive notifications when the app is minimized
- **Keyboard Shortcuts**: Quick access to common actions
- **Secure HTTP**: Uses Rust's reqwest for secure API communication
- **Local Storage**: Data persists between sessions
- **Drag & Drop Import**: Drop JSON backup files directly into the app

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| New Chat | Ctrl + N | ⌘ + N |
| Settings | Ctrl + , | ⌘ + , |
| Export All Data | Ctrl + E | ⌘ + E |
| Export Current Chat | Ctrl + Shift + E | ⌘ + ⇧ + E |
| Toggle Dark Mode | Ctrl + D | ⌘ + D |
| Show Shortcuts | Ctrl + / | ⌘ + / |

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Rust](https://rustup.rs/) (latest stable)
- Platform-specific dependencies:
  - **Windows**: Visual Studio Build Tools with C++ workload
  - **macOS**: Xcode Command Line Tools (`xcode-select --install`)
  - **Linux**: `sudo apt install libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf`

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Build Frontend

The frontend is built from the main `index.html` in the parent directory:

```bash
./build-frontend.sh
```

### 3. Development Mode

Run the app in development mode with hot reload:

```bash
npm run dev
```

### 4. Build for Production

Build the app for your current platform:

```bash
npm run build
```

Built applications will be in `src-tauri/target/release/bundle/`.

## Project Structure

```
tauri-client/
├── dist/                    # Frontend files (built from parent index.html)
│   ├── index.html          # Main HTML (generated)
│   ├── tauri-bridge.js     # Tauri API integration layer
│   ├── desktop-styles.css  # Desktop-specific styles
│   └── desktop-init.js     # Desktop initialization script
├── src-tauri/              # Rust backend
│   ├── src/
│   │   └── main.rs         # Tauri application entry point
│   ├── Cargo.toml          # Rust dependencies
│   ├── tauri.conf.json     # Tauri configuration
│   └── capabilities/       # Security permissions
├── package.json            # Node.js configuration
├── build-frontend.sh       # Frontend build script
└── README.md               # This file
```

## Configuration

### API Endpoints

Configure API endpoints through the Settings panel (Ctrl/⌘ + ,). The app supports multiple endpoints with:
- Custom names
- API keys (optional)
- User GUIDs
- Environment tags (local, development, staging, production)

### Azure TTS

Voice synthesis requires Azure Cognitive Services:
1. Get an Azure Speech API key
2. Configure in Settings > Voice tab
3. Select your preferred voice

## Security

- All API requests go through Tauri's secure HTTP client
- No browser-based CORS restrictions
- API keys are stored locally (never transmitted to third parties)
- Files are written only to user-authorized locations

## Troubleshooting

### Build Fails

1. Ensure Rust is installed and up to date:
   ```bash
   rustup update stable
   ```

2. Clear the build cache:
   ```bash
   cd src-tauri && cargo clean
   ```

3. Rebuild:
   ```bash
   npm run build
   ```

### App Won't Start

1. Check the console for errors (in development mode)
2. Ensure all dependencies are installed
3. Verify the `dist/index.html` exists

### No Sound/Voice

1. Verify Azure TTS credentials in Settings
2. Check that your system audio is working
3. Try a different voice in the Voice settings

## Development

### Adding Native Features

1. Add Rust functions in `src-tauri/src/main.rs`
2. Register commands in the `invoke_handler`
3. Call from JavaScript using `TauriBridge` or `window.__TAURI__.core.invoke`

### Modifying the Frontend

The frontend is built from the parent `index.html`. To modify:
1. Edit the source `../index.html`
2. Run `./build-frontend.sh` to rebuild
3. Desktop-specific enhancements are in `dist/desktop-init.js`

## License

MIT License - See LICENSE file for details.

## Credits

Built with:
- [Tauri](https://tauri.app/) - Desktop application framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - AI backend
- [Azure Speech Services](https://azure.microsoft.com/en-us/products/ai-services/ai-speech) - Text-to-speech
