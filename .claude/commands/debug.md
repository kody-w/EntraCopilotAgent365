# Debug Copilot Agent 365

You are debugging an issue with Copilot Agent 365. Systematically diagnose the problem.

## Debugging Workflow

### 1. Identify the Error Type

**"An error occurred. Please try again."**
- OpenAI API call is failing
- Check `function_app.py` around line 830 for error details
- Common causes: wrong API format, auth issues, model not found

**401 Unauthorized**
- Missing or invalid function key
- Get new key: `az functionapp function keys list --name copilot365-4ovzneuimhd2g --resource-group rappai --function-name main`

**500 Internal Server Error**
- Check Azure logs: `az functionapp log tail --name copilot365-4ovzneuimhd2g --resource-group rappai`
- Usually agent loading or storage initialization failure

**CORS Error**
- Check `build_cors_response()` in function_app.py
- Verify host.json has CORS configured

### 2. Check Key Components

**OpenAI API Format** (must use tools, not functions):
```python
# CORRECT
tools=[{"type": "function", "function": func} for func in agent_metadata]
tool_choice="auto"

# WRONG (deprecated)
functions=agent_metadata
function_call="auto"
```

**Response Handling** (must use tool_calls, not function_call):
```python
# CORRECT
if assistant_msg.tool_calls:
    tool_call = assistant_msg.tool_calls[0]
    agent_name = tool_call.function.name

# WRONG (deprecated)
if assistant_msg.function_call:
    agent_name = assistant_msg.function_call.name
```

**Tool Result Message Format**:
```python
# CORRECT
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result
})

# WRONG (deprecated)
messages.append({
    "role": "function",
    "name": agent_name,
    "content": result
})
```

### 3. Check Environment Variables

Required in Azure (and local.settings.json):
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_FILES_SHARE_NAME`

### 4. Test Locally First

```bash
source .venv/bin/activate
func start
# Then test with curl to localhost:7071
```

### 5. Check Agent Loading

Agents load from:
1. Local `agents/` folder
2. Azure File Storage `agents/` share
3. Azure File Storage `multi_agents/` share

If agent not found, check:
- File has `.py` extension
- Class inherits from `BasicAgent`
- Has `name`, `metadata`, and `perform()` method

## User's Issue
$ARGUMENTS
