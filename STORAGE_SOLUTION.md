# Environment-Aware Storage Solution

## Problem Solved

**Original Issue:** Azure Files with token-based authentication fails when key-based auth is disabled on the storage account, blocking local development.

**Solution:** Implemented environment-aware storage that gracefully degrades to local file system storage for development while maintaining Azure File Storage for production.

## Architecture

### Components Created

1. **`utils/environment.py`** - Environment detection utilities
   - `is_running_in_azure()` - Detects Azure deployment
   - `should_use_azure_storage()` - Determines storage backend
   - `get_local_storage_path()` - Returns local storage directory

2. **`utils/local_file_storage.py`** - Local storage implementation
   - `LocalFileStorageManager` - Drop-in replacement for Azure storage
   - Implements identical interface to `AzureFileStorageManager`
   - Uses `.local_storage/` directory in project root

3. **`utils/storage_factory.py`** - Storage factory pattern
   - `get_storage_manager()` - Returns appropriate storage backend
   - `create_storage_manager_safe()` - Safe initialization with fallback

4. **Updated Components:**
   - `function_app.py` - Uses storage factory
   - All agents - Updated to use storage factory
   - `.gitignore` - Excludes `.local_storage/`

## How It Works

### Automatic Detection

```
┌─────────────────────────────────────┐
│   Application Starts                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   get_storage_manager() called      │
└──────────────┬──────────────────────┘
               │
               ▼
       ┌───────────────┐
       │ Environment?  │
       └───────┬───────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────┐    ┌──────────────┐
│  Azure   │    │    Local     │
│  Env?    │    │ Azure Config?│
└────┬─────┘    └──────┬───────┘
     │                 │
     │ Yes         No  │ Yes
     │                 │
     ▼                 ▼
┌─────────────┐  ┌──────────────┐
│   Azure     │  │    Azure     │
│  Storage    │  │   Storage    │
└─────────────┘  └──────────────┘
                       │
                   No  │
                       ▼
              ┌─────────────────┐
              │ Local File      │
              │ Storage         │
              └─────────────────┘
```

### Storage Interface

Both implementations provide identical methods:

```python
class StorageManager:
    # Memory operations
    def set_memory_context(self, guid: Optional[str]) -> bool
    def read_json(self) -> dict
    def write_json(self, data: dict)

    # File operations
    def write_file(self, directory: str, filename: str, content: Union[str, bytes]) -> bool
    def read_file(self, directory: str, filename: str) -> Optional[Union[str, bytes]]
    def read_file_binary(self, directory: str, filename: str) -> Optional[bytes]
    def list_files(self, directory: str) -> List
    def delete_file(self, directory: str, filename: str) -> bool
    def file_exists(self, directory: str, filename: str) -> bool
    def get_file_properties(self, directory: str, filename: str) -> Optional[dict]

    # Directory operations
    def ensure_directory_exists(self, directory: str) -> bool

    # URL generation
    def generate_download_url(self, directory: str, filename: str, expiry_minutes: int) -> Optional[str]
```

## Usage

### In Application Code

```python
# Old way (hardcoded)
from utils.azure_file_storage import AzureFileStorageManager
storage = AzureFileStorageManager()  # ❌ Fails without Azure credentials

# New way (environment-aware)
from utils.storage_factory import get_storage_manager
storage = get_storage_manager()  # ✅ Works everywhere
```

### Running Locally

**Without Azure Credentials:**
```bash
# No configuration needed
./run.sh

# Storage automatically uses .local_storage/
# All features work identically
```

**With Azure Credentials:**
```bash
# Configure local.settings.json with Azure credentials
# Storage automatically uses Azure Files
# Shares state with deployed function app
```

### In Production (Azure)

```bash
# Deploy to Azure
./deploy.sh

# Storage automatically uses Azure Files
# Environment variables pre-configured
```

## Local Storage Structure

```
.local_storage/
├── shared_memories/          # Shared memory context
│   └── memory.json
├── memory/                   # User-specific memories
│   └── {user-guid}/
│       └── user_memory.json
├── agents/                   # Custom agent files
│   └── *.py
├── multi_agents/             # Multi-agent orchestrators
│   └── *.py
├── demos/                    # Demo scripts
│   └── *.json
├── agent_config/             # Per-user agent configs
│   └── {user-guid}/
│       └── enabled_agents.json
└── test_agents/              # Test directory
    └── *.py
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_local_storage.py
```

Tests verify:
- Environment detection
- Storage initialization
- Memory operations (shared and user-specific)
- File operations (read, write, list, delete)
- Storage location and structure

## Migration Path

### Existing Deployments

No changes needed for existing Azure deployments:
- Environment detection automatically uses Azure storage
- All environment variables remain the same
- No breaking changes to API or behavior

### Local Development

Developers can now work without Azure credentials:
1. Clone repository
2. Run `./run.sh`
3. Storage automatically uses `.local_storage/`
4. All features work identically

## Benefits

### For Developers

- **Zero-config local development** - No Azure credentials required
- **Faster iteration** - No network latency for storage operations
- **Easy debugging** - Files visible in `.local_storage/` directory
- **Offline development** - Work without internet connection

### For DevOps

- **Same codebase** - No environment-specific code branches
- **Graceful degradation** - Auth failures don't break local dev
- **Easy testing** - Test locally before deploying to Azure
- **No credential management** - Local storage doesn't need secrets

### For Production

- **No changes** - Azure deployments work identically
- **Performance** - Azure Files for production workloads
- **Scalability** - Shared storage across function instances
- **Reliability** - Persistent storage with Azure SLA

## Error Handling

### Azure Storage Fails

```python
try:
    storage = get_storage_manager()
except Exception as e:
    # In Azure: Critical error, propagate
    if is_running_in_azure():
        raise
    # In local: Fall back to local storage
    storage = LocalFileStorageManager()
```

### Local Storage Issues

- Directory creation failures → Logged and raised
- Permission issues → Logged with clear error message
- Missing files → Returns None (consistent with Azure)

## Performance

### Local Storage

- **Read:** Direct file system access (~1ms)
- **Write:** Direct file system access (~5ms)
- **List:** Directory scan (~10ms)

### Azure Storage

- **Read:** Network + Azure Files API (~50-200ms)
- **Write:** Network + Azure Files API (~100-300ms)
- **List:** Network + Azure Files API (~100-500ms)

Local storage provides 10-100x faster operations for development.

## Security

### Local Storage

- Files stored in `.local_storage/` directory
- Directory excluded from git via `.gitignore`
- Permissions inherited from project directory
- Not suitable for production (no encryption, no access control)

### Azure Storage

- Managed Identity or SAS token authentication
- Encryption at rest and in transit
- Azure RBAC for access control
- Audit logging via Azure Monitor
- Production-ready security

## Troubleshooting

### Issue: Storage fails in Azure

**Symptoms:** Storage initialization fails in deployed function
**Diagnosis:** Check environment variables are set correctly
**Solution:** Verify `AZURE_STORAGE_ACCOUNT_NAME` and `AZURE_FILES_SHARE_NAME`

### Issue: Local storage not persisting

**Symptoms:** Data disappears between runs
**Diagnosis:** Check `.local_storage/` directory exists and is writable
**Solution:**
```bash
chmod -R u+w .local_storage/
```

### Issue: Wrong storage backend used

**Symptoms:** Expecting local but using Azure (or vice versa)
**Diagnosis:** Check detection logic in logs
**Solution:** Review environment variables and detection criteria

## Future Enhancements

### Possible Extensions

1. **In-Memory Storage** - For unit tests
2. **S3 Storage** - For AWS deployments
3. **Redis Storage** - For distributed caching
4. **Hybrid Storage** - Local cache + remote persistence

### Implementation Pattern

```python
class InMemoryStorageManager:
    """Memory-only storage for unit tests"""
    def __init__(self):
        self.data = {}

# In storage_factory.py
def get_storage_manager():
    if os.environ.get('UNIT_TEST_MODE'):
        return InMemoryStorageManager()
    # ... existing logic
```

## Documentation

- **Setup Guide:** See `docs/LOCAL_DEVELOPMENT.md`
- **API Reference:** See docstrings in storage classes
- **Architecture:** This file
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`

## Code Changes Summary

### Files Created
- `utils/environment.py` (96 lines)
- `utils/local_file_storage.py` (473 lines)
- `utils/storage_factory.py` (46 lines)
- `test_local_storage.py` (348 lines)
- `docs/LOCAL_DEVELOPMENT.md` (572 lines)
- `STORAGE_SOLUTION.md` (this file)

### Files Modified
- `function_app.py` (3 changes)
- `agents/context_memory_agent.py` (2 changes)
- `agents/manage_memory_agent.py` (2 changes)
- `agents/github_agent_library_manager.py` (2 changes)
- `agents/scripted_demo_agent.py` (2 changes)
- `.gitignore` (1 addition)

### Total Changes
- **Lines Added:** ~1,600
- **Lines Modified:** ~15
- **Files Modified:** 6
- **Files Created:** 6
- **Breaking Changes:** 0

## Verification

Run these commands to verify the solution:

```bash
# 1. Run test suite
python3 test_local_storage.py

# 2. Check local storage created
ls -la .local_storage/

# 3. Start function app (uses local storage)
./run.sh

# 4. Test API endpoint
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

## Summary

This solution provides:

✅ **Zero-config local development** - Works without Azure credentials
✅ **Identical interface** - Same code for all environments
✅ **Automatic detection** - Chooses correct storage backend
✅ **Graceful degradation** - Falls back when Azure unavailable
✅ **No breaking changes** - Existing deployments unaffected
✅ **Comprehensive testing** - Full test suite included
✅ **Production-ready** - Azure storage for deployed apps
✅ **Developer-friendly** - Fast local iteration

The storage system is now **environment-aware, robust, and developer-friendly** while maintaining **production reliability and performance**.
