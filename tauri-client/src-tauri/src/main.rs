// Prevents additional console window on Windows in release
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::{Manager, AppHandle};

#[derive(Debug, Serialize, Deserialize)]
struct ChatMessage {
    role: String,
    content: String,
    timestamp: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiRequest {
    user_input: String,
    conversation_history: Vec<ChatMessage>,
    user_guid: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse {
    assistant_response: String,
    voice_response: Option<String>,
    agent_logs: Option<String>,
    user_guid: Option<String>,
}

/// Get the application data directory for storing local files
#[tauri::command]
fn get_app_data_dir(app: AppHandle) -> Result<String, String> {
    app.path()
        .app_data_dir()
        .map(|p| p.to_string_lossy().to_string())
        .map_err(|e| e.to_string())
}

/// Export chat data to a file
#[tauri::command]
async fn export_data(path: String, data: String) -> Result<(), String> {
    fs::write(&path, data).map_err(|e| format!("Failed to export data: {}", e))
}

/// Import chat data from a file
#[tauri::command]
async fn import_data(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| format!("Failed to import data: {}", e))
}

/// Send a chat message to the API endpoint with native HTTP client
#[tauri::command]
async fn send_chat_message(
    endpoint_url: String,
    api_key: Option<String>,
    user_input: String,
    conversation_history: Vec<ChatMessage>,
    user_guid: Option<String>,
) -> Result<ApiResponse, String> {
    let client = reqwest::Client::new();

    let request = ApiRequest {
        user_input,
        conversation_history,
        user_guid,
    };

    let mut request_builder = client
        .post(&endpoint_url)
        .header("Content-Type", "application/json")
        .json(&request);

    if let Some(key) = api_key {
        if !key.is_empty() {
            request_builder = request_builder.header("x-functions-key", key);
        }
    }

    let response = request_builder
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("API error: HTTP {}", response.status()));
    }

    response
        .json::<ApiResponse>()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))
}

/// Test endpoint connectivity
#[tauri::command]
async fn test_endpoint(endpoint_url: String, api_key: Option<String>) -> Result<bool, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(5))
        .build()
        .map_err(|e| e.to_string())?;

    let request = ApiRequest {
        user_input: "ping".to_string(),
        conversation_history: vec![],
        user_guid: None,
    };

    let mut request_builder = client
        .post(&endpoint_url)
        .header("Content-Type", "application/json")
        .json(&request);

    if let Some(key) = api_key {
        if !key.is_empty() {
            request_builder = request_builder.header("x-functions-key", key);
        }
    }

    let response = request_builder.send().await.map_err(|e| e.to_string())?;

    Ok(response.status().is_success())
}

/// Get system information
#[tauri::command]
fn get_system_info() -> Result<serde_json::Value, String> {
    Ok(serde_json::json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "family": std::env::consts::FAMILY,
    }))
}

/// Show native notification
#[tauri::command]
async fn show_notification(app: AppHandle, title: String, body: String) -> Result<(), String> {
    use tauri_plugin_notification::NotificationExt;

    app.notification()
        .builder()
        .title(&title)
        .body(&body)
        .show()
        .map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_os::init())
        .invoke_handler(tauri::generate_handler![
            get_app_data_dir,
            export_data,
            import_data,
            send_chat_message,
            test_endpoint,
            get_system_info,
            show_notification,
        ])
        .setup(|app| {
            // Create app data directory if it doesn't exist
            if let Ok(app_data_dir) = app.path().app_data_dir() {
                let _ = fs::create_dir_all(&app_data_dir);
            }

            // Set up any additional initialization here
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
