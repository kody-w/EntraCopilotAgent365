# Deploy Copilot Agent 365

You are deploying the Copilot Agent 365 project to Azure. Follow this checklist:

## Pre-Deployment Checklist

1. **Run all tests first** - Never deploy without testing
2. **Check for secrets** - Ensure no API keys in code
3. **Verify local.settings.json** - Has correct Azure credentials

## Deployment Steps

Execute these steps in order:

### Step 1: Run Pre-Deployment Tests
```bash
python run_pre_deployment_tests.py
```
**STOP if any tests fail** - fix issues before deploying.

### Step 2: Verify No Secrets in Code
```bash
# Check for potential secrets
grep -r "xGkEFEbTuX\|AccountKey=\|api[_-]key.*=" --include="*.py" --include="*.json" . 2>/dev/null | grep -v ".venv" | grep -v "local.settings"
```
Should return empty. If not, remove secrets before deploying.

### Step 3: Deploy to Azure
```bash
source .venv/bin/activate
func azure functionapp publish copilot365-4ovzneuimhd2g --python
```

### Step 4: Verify Deployment
```bash
# Get function key
az functionapp function keys list --name copilot365-4ovzneuimhd2g --resource-group rappai --function-name main -o tsv --query default

# Test endpoint (replace YOUR_KEY)
curl -s -X POST 'https://copilot365-4ovzneuimhd2g.azurewebsites.net/api/businessinsightbot_function?code=YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"user_input": "Hello", "conversation_history": []}'
```

### Step 5: Monitor Logs (if issues)
```bash
az functionapp log tail --name copilot365-4ovzneuimhd2g --resource-group rappai
```

## Target Environment
- **Function App**: copilot365-4ovzneuimhd2g
- **Resource Group**: rappai
- **Region**: East US 2

## Additional Context
$ARGUMENTS
