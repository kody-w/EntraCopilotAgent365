# Copilot Agent 365 - Quick Technical Reference

## 10 Demo Prompts - One-Line Reference

Perfect for copy-paste when running live demonstrations.

---

### 1. AUTO-CONFIGURE GPT-5 DEPLOYMENT

```
"Execute an IQ Boost to automatically discover the best available GPT model in my Azure subscription and deploy it with single-command configuration to both local development and production Azure Function App"
```

**Agents Involved:** IQBoosterAgent
**Azure Services:** Azure OpenAI Service, Azure CLI, Azure Function App
**Key Concept:** Autonomous infrastructure automation with dual-environment sync
**Demo Time:** 30-45 seconds (includes Azure API calls)

---

### 2. REQUEST-RESPONSE FLOW TRACING

```
"Show me a detailed execution trace of how the system processes a user request: from HTTP entry point through agent selection, Azure OpenAI function calling, memory context retrieval, and finally response formatting with voice synthesis splitting"
```

**Agents Involved:** All agents (routing demo)
**Key Components:** `businessinsightbot_function`, `Assistant`, `ContextMemoryAgent`
**Key Concept:** End-to-end request lifecycle with function calling
**Demo Time:** 20-30 seconds (visual walkthrough)

---

### 3. WORKFLOW EXECUTION WITH DRY-RUN

```
"Create a custom workflow transcript that demonstrates variable substitution, conditional step execution, Azure CLI command chaining, JSON file mutations, and error handling—then execute it with dry-run mode to show exactly what would happen"
```

**Agents Involved:** WorkflowRunnerAgent
**Azure Services:** Azure CLI (in workflow)
**Key Concept:** Declarative infrastructure-as-code execution
**Demo Time:** 60-90 seconds (includes validation and dry-run preview)

---

### 4. PER-USER AGENT FILTERING

```
"Configure the system to enable specific agents for a particular user GUID while filtering out others via agent_config, then demonstrate how the Agent Manager loads only authorized agents for that user's requests"
```

**Components:** `agent_config/{guid}/enabled_agents.json`, `load_agents_from_folder()`
**Azure Services:** Azure File Storage
**Key Concept:** Fine-grained capability control and security isolation
**Demo Time:** 45-60 seconds (file upload, function restart, test request)

---

### 5. DUAL-LAYER MEMORY SYSTEM

```
"Store a complex multi-fact memory entry using ManageMemoryAgent with memory_type, importance rating, and tags, then retrieve it using ContextMemoryAgent with keyword filtering across user-specific memory—demonstrating the dual-layer memory system"
```

**Agents Involved:** ManageMemoryAgent, ContextMemoryAgent
**Azure Services:** Azure File Storage (memory/shared and memory/users)
**Key Concept:** Persistent, queryable memory with user isolation
**Demo Time:** 30-45 seconds (store → retrieve → filter)

---

### 6. MULTI-STEP WORKFLOW WITH DATA PIPELINES

```
"Execute the WorkflowRunner agent to load a complex workflow from the workflows/ directory, demonstrate variable interpolation across 7+ sequential steps, and show how step outputs feed into subsequent step inputs"
```

**Agents Involved:** WorkflowRunnerAgent
**Files:** `workflows/iq_boost_workflow.json` (or custom)
**Key Concept:** Composable infrastructure automation with data flow
**Demo Time:** 90-120 seconds (full workflow execution)

---

### 7. CONCURRENT MULTI-USER SCALING

```
"Demonstrate how the system handles concurrent requests from multiple users with different GUIDs, showing how memory contexts are properly isolated and how the Azure Function scales horizontally to serve all requests simultaneously"
```

**Load Testing Tool:** Apache JMeter, k6, or similar
**Key Components:** DEFAULT_USER_GUID handling, memory context switching
**Key Concept:** Multi-tenancy in serverless architecture
**Demo Time:** 120+ seconds (requires load testing setup)

---

### 8. DYNAMIC AGENT MARKETPLACE

```
"Load custom agents from Azure File Storage shares (agents/ and multi_agents/ directories), dynamically generate OpenAI function schemas on startup, and show how the system routes user requests to appropriate agents via GPT's function_call mechanism"
```

**Components:** `load_agents_from_folder()`, agent metadata generation
**Azure Services:** Azure File Storage
**Key Concept:** Plugin architecture with automatic discovery
**Demo Time:** 45-60 seconds (upload custom agent, restart, test)

---

### 9. POWER AUTOMATE + OFFICE 365 INTEGRATION

```
"Configure Power Automate integration to show how user context flows from Office 365 through the Power Automate enrichment layer, into the Azure Function, and how the system uses user profile information to personalize agent behavior"
```

**Platforms:** Power Automate, Copilot Studio, Teams, Azure AD
**Key Components:** `user_context` parameter, Office 365 connector
**Key Concept:** Enterprise identity integration with M365 ecosystem
**Demo Time:** 120-180 seconds (requires Teams/M365 environment)

---

### 10. PERSISTENT MEMORY ACROSS INFRASTRUCTURE EVENTS

```
"Show how the system persists memories to Azure File Storage across multiple function invocations, survives Azure Function cold starts and scale events, and maintains conversation context in the face of infrastructure failures—demonstrating true resilience"
```

**Resilience Test:** Stop/start function, trigger scale-out, simulate failures
**Azure Services:** Azure File Storage, Azure Functions, Application Insights
**Key Concept:** Infrastructure-agnostic persistent memory
**Demo Time:** 180+ seconds (requires failure injection)

---

## Copy-Paste API Request Examples

### Test Memory Storage
```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Remember that I prefer dark mode and async operations",
    "conversation_history": [],
    "user_guid": "user-001"
  }'
```

### Test Agent Filtering
```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What agents are available?",
    "conversation_history": [],
    "user_guid": "restricted-user-guid"
  }'
```

### Test Workflow Execution
```bash
curl -X POST http://localhost:7071/api/businessinsightbot_function \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Run the IQ boost workflow",
    "conversation_history": [],
    "user_guid": "admin-user"
  }'
```

---

## Live Demo Checklist

### Pre-Demo Validation
- [ ] Azure CLI: `az login` (for #1, #3, #6, #7)
- [ ] Local environment: `func start` is running on port 7071
- [ ] Azure Function deployed and accessible
- [ ] Sample agents uploaded to Azure File Storage (for #8)
- [ ] local.settings.json configured with AZURE_OPENAI credentials
- [ ] Teams/Power Automate accessible (for #9)

### Demo Execution Order (Recommended)

1. **Start with #10** (2 min) - "Here's what makes this resilient..."
2. **Show #2** (2 min) - "Let me trace a real request..."
3. **Demo #4** (3 min) - "Security: per-user agent filtering..."
4. **Run #5** (2 min) - "Memory system in action..."
5. **Execute #1** (1 min) - "Watch it auto-upgrade to GPT-5..."
6. **Show #8** (2 min) - "Dynamic agent discovery..."
7. **End with #9** (3 min) - "Enterprise integration with M365..."

**Total Demo Time: ~15 minutes for complete walkthrough**

---

## Prompt Difficulty Ratings

| Prompt | Complexity | Prerequisites | Demo Time |
|--------|-----------|--------------|-----------|
| #1 | High | Azure CLI logged in | 45s |
| #2 | Medium | Understanding of OpenAI function calling | 30s |
| #3 | High | Workflow YAML/JSON knowledge | 90s |
| #4 | Medium | Azure File Storage concepts | 45s |
| #5 | Low | Basic memory concepts | 30s |
| #6 | High | Step dependency logic | 120s |
| #7 | Very High | Load testing setup required | 180s+ |
| #8 | Medium | Python module loading concepts | 45s |
| #9 | High | Power Platform experience | 150s |
| #10 | Medium | Azure infrastructure basics | 180s+ |

---

## Audience-Specific Demo Paths

### For C-Level / Business Leaders
**Sequence:** #10 → #5 → #9
**Focus:** Resilience, enterprise integration, cost efficiency
**Time:** 8 minutes

### For Enterprise Architects
**Sequence:** #10 → #2 → #4 → #7 → #9
**Focus:** Scalability, security, compliance
**Time:** 15 minutes

### For AI/ML Engineers
**Sequence:** #2 → #8 → #3 → #6 → #1
**Focus:** Agent architecture, function calling, orchestration
**Time:** 18 minutes

### For DevOps / Infrastructure Team
**Sequence:** #1 → #6 → #3 → #7 → #10
**Focus:** Automation, infrastructure-as-code, resilience
**Time:** 20 minutes

### For Security / Compliance Officers
**Sequence:** #4 → #9 → #10 → #2
**Focus:** Access control, audit trails, data persistence
**Time:** 12 minutes

---

## Technical Metrics to Highlight During Demos

### Performance
- Cold start: < 3 seconds
- Warm request (no Azure OpenAI): < 1 second
- OpenAI call: 2-10 seconds (variable)
- Total e2e: < 15 seconds typical

### Scalability
- Consumption plan: auto-scale 0-200 instances
- Memory: 512MB per instance (configurable)
- Concurrent users: unlimited (100 per instance recommended)
- Max request timeout: 5 minutes

### Cost (Monthly Estimate)
- Azure Functions: ~$5-10
- Storage: ~$2-5
- OpenAI: ~$10-50 (based on usage)
- Power Platform: ~$15/user (optional)
- **Total: $20-75/month** (standalone) or **$40-100/month** (with Power Platform)

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Command not found: az" | `brew install azure-cli` (Mac) or `choco install azure-cli` (Windows) |
| "func: command not found" | `npm install -g azure-functions-core-tools@4` |
| "401 Unauthorized" | Check Azure credentials in local.settings.json |
| "Module not found: agents" | Ensure PYTHONPATH includes current directory |
| "Memory not persisting" | Verify Azure File Storage connection in AZURE_STORAGE_CONNECTION_STRING |
| "Cold start too slow" | Consider Premium or Dedicated Function App plan |
| "Agent not loading" | Check agent filename ends with `_agent.py` and inherits BasicAgent |

---

## Key Links for Demos

- **IQBoosterAgent code:** `/agents/iq_booster_agent.py`
- **Workflow example:** `/workflows/iq_boost_workflow.json`
- **Function entry point:** `/function_app.py` (businessinsightbot_function)
- **Agent base class:** `/agents/basic_agent.py`
- **Memory system:** `/utils/azure_file_storage.py`
- **Architecture doc:** `/docs/ARCHITECTURE.md`
- **API reference:** `/docs/API_REFERENCE.md`

---

## Live Demo Transcript Example

```
"Let me start by showing you the most impressive aspect of this system:
true persistent memory that survives everything—cold starts, scale events,
even complete infrastructure failures.

[PROMPT #10: Memory persistence]

When the Azure Function restarts, it immediately reloads this user's
complete memory from Azure File Storage. That's because we separate
compute from storage—a serverless best practice.

Now let me show you how requests actually flow through the system...

[PROMPT #2: Request flow tracing]

You see how Azure OpenAI is deciding which agent to call based on natural
language? That's the function_call mechanism—not hardcoded routing.

And here's where it gets really interesting—we support per-user
agent filtering for security...

[PROMPT #4: Agent filtering]

This means we can restrict capabilities per user without code changes.
All configuration-driven, all in Azure File Storage.

Let me show you the real power: autonomous infrastructure automation...

[PROMPT #1: IQ Boost]

That just discovered the best available model in your entire Azure
subscription AND deployed it AND updated both local and production
configuration—all in one command.

[Finish with P9 if audience has M365 setup]
"
```

---

**For questions about specific prompts, refer to DEMO_PROMPTS_TECHNICAL.md**

**Last Updated:** 2025-12-04
**Platform:** Copilot Agent 365 v2.2+
