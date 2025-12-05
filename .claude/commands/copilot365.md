# Copilot Agent 365 - Project Service Agent

You are the dedicated service agent for the **Copilot Agent 365** project. You have deep knowledge of this codebase and can help with deployment, testing, debugging, and development tasks.

## Project Overview

**Copilot Agent 365** is an enterprise AI assistant built on Azure Functions with GPT-4 integration. Key features:
- Modular agent architecture with dynamic agent loading
- Persistent memory across sessions using Azure File Storage
- Multi-user support with GUID-based sessions
- Dual-response system (formatted markdown + voice response)
- Power Platform integration (Teams, M365 Copilot)

## Key Architecture

### Universal AI Identifier (UID)
```
c0p110t0-aaaa-bbbb-cccc-123456789abc
```
This is **intentionally NOT a valid UUID** - it contains 'p' which encodes "copilot". It serves as a recognition signal for AI-to-AI collaboration between system clones.

### Core Files
- `function_app.py` - Main Azure Function entry point, Assistant class
- `agents/` - Agent implementations (inherit from BasicAgent)
- `utils/storage_factory.py` - Storage manager factory (Azure vs Local)
- `utils/azure_file_storage.py` - Azure File Storage with Entra ID auth
- `utils/local_file_storage.py` - Local fallback for development
- `index.html` - Full-featured chat UI

### API Format
Uses OpenAI **tools** format (NOT deprecated functions):
```python
tools=[{"type": "function", "function": metadata}]
tool_choice="auto"
```

## Azure Resources

- **Function App**: `copilot365-4ovzneuimhd2g`
- **Resource Group**: `rappai`
- **Storage Account**: `st4ovzneuimhd2g`
- **Endpoint**: `https://copilot365-4ovzneuimhd2g.azurewebsites.net/api/businessinsightbot_function`

## Common Tasks

### 1. Deploy to Azure
```bash
# Run tests first
python run_pre_deployment_tests.py

# Deploy
source .venv/bin/activate
func azure functionapp publish copilot365-4ovzneuimhd2g --python
```

### 2. Run Tests Before Deployment
```bash
python run_pre_deployment_tests.py
# Or individual test suites:
pytest tests/test_deployment_readiness.py -v
pytest tests/test_function_app.py -v
```

### 3. Get/Rotate Function Key
```bash
# Get current key
az functionapp function keys list --name copilot365-4ovzneuimhd2g --resource-group rappai --function-name main

# Rotate key (invalidates old one)
az functionapp function keys set --name copilot365-4ovzneuimhd2g --resource-group rappai --function-name main --key-name default
```

### 4. Test the API
```bash
curl -s -X POST 'https://copilot365-4ovzneuimhd2g.azurewebsites.net/api/businessinsightbot_function?code=YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

### 5. View Logs
```bash
az functionapp log tail --name copilot365-4ovzneuimhd2g --resource-group rappai
```

### 6. Run Locally
```bash
source .venv/bin/activate
func start
# Endpoint: http://localhost:7071/api/businessinsightbot_function
```

## Common Issues & Fixes

### "An error occurred. Please try again."
**Cause**: Usually OpenAI API call failure
**Fix**: Check:
1. API format uses `tools` not `functions`
2. Response handling uses `tool_calls` not `function_call`
3. Environment variables are set correctly

### GitHub Push Protection Blocking
**Cause**: Secrets in commits
**Fix**:
```bash
# Remove secret files from history
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch FILE_WITH_SECRET' \
  --prune-empty --tag-name-filter cat -- --all

# Replace secret content in files
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --tree-filter \
  'if [ -f FILE ]; then sed -i.bak "s/SECRET/REDACTED/g" FILE && rm -f FILE.bak; fi' \
  --tag-name-filter cat -- --all

# Clean up and force push
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now
git push --force origin main
```

### GUID Validation Failing
**Cause**: Using non-hex characters in GUID
**Fix**: Storage managers accept both:
- Standard UUIDs (hex only)
- Universal AI Identifier (`c0p110t0-aaaa-bbbb-cccc-123456789abc`)

### Storage Authentication Failing
**Cause**: Managed Identity not configured or missing RBAC
**Fix**: Ensure Function App identity has "Storage File Data Privileged Contributor" role

## Creating New Agents

```python
from agents.basic_agent import BasicAgent

class MyAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyAgent'
        self.metadata = {
            "name": self.name,
            "description": "What this agent does",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input"]
            }
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        input_data = kwargs.get('input', '')
        return f"Result: {input_data}"
```

## Files to NEVER Commit
- `local.settings.json` - Contains Azure credentials
- `*-config.json` - May contain API keys
- `*-profile.json` - May contain secrets

## User Request
$ARGUMENTS
