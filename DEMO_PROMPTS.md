# Copilot Agent 365 - Demo Prompts: Automation & Self-Management

**Strategy Focus:** Prompts that showcase the system automatically managing itself, discovering resources, configuring infrastructure, running workflows, and eliminating manual work entirely.

---

## Demo Prompts (Auto-Automation Focused)

### 1. "Boost my AI to the latest model"
- **Automation:** IQ Booster Agent auto-discovers all Azure OpenAI resources in the subscription, identifies the best available model (gpt-5-chat, gpt-4o, etc.), automatically deploys it if missing, updates Azure Function App production settings, AND updates local.settings.json for development—all without user intervention or manual resource management.

### 2. "Set up my agent library with sales team capabilities"
- **Automation:** GitHub Agent Library Manager auto-discovers the entire 65+ agent repository, searches for sales-specific agents, fetches code from GitHub, installs them to Azure File Storage, creates a GUID-based agent group, and registers them as callable functions—zero manual downloading, copying, or configuration of individual agent files.

### 3. "Run our deployment workflow automatically"
- **Automation:** Workflow Runner Agent loads the JSON workflow transcript, auto-substitutes all variables (function app names, resource groups, endpoints), executes each step in sequence, captures outputs from each step for use in the next step, logs all changes, and handles errors with fallback actions—no manual command execution or script editing needed.

### 4. "Discover what Azure OpenAI resources I have and what models are available"
- **Automation:** IQ Booster Agent auto-scans the entire Azure subscription, lists all OpenAI resources with their locations and SKUs, discovers available model types, shows current deployments, displays quotas, and provides instant recommendations—zero Azure portal navigation required.

### 5. "Install a custom email agent and enable it just for my team"
- **Automation:** GitHub Agent Library Manager auto-finds the email agent from the public repository, downloads the Python code, installs it to Azure File Storage, creates a user group for your team's GUID, adds the agent to that group's enabled_agents.json, and makes it immediately available—no file transfers or manual configuration needed.

### 6. "Check my current AI configuration and fix any issues automatically"
- **Automation:** IQ Booster Agent auto-reads local.settings.json and Azure Function App settings, validates all Azure OpenAI endpoints and API keys, checks model deployment status, auto-updates any stale configurations, verifies file shares exist, and reports all fixes made—no manual verification or Azure portal checks needed.

### 7. "Update all my configuration values to use the new Azure endpoint"
- **Automation:** IQ Booster Agent auto-discovers the new Azure OpenAI endpoint in the subscription, updates the deployment configuration, applies changes to Azure Function App (production), updates local.settings.json (development), restarts the function app automatically, and confirms the new endpoint is active—zero manual updates to multiple files.

### 8. "Run a workflow to deploy my latest agents and test them"
- **Automation:** Workflow Runner Agent loads the deployment workflow, auto-discovers agents in the agents/ and multi_agents/ folders, executes the upload-to-Azure-Storage step, runs integration tests using mock requests, captures test results in variables, triggers on_complete actions if all pass, OR on_error handlers if failures occur—no manual testing or deployment steps.

### 9. "Install all agents from the manufacturing vertical and organize them by category"
- **Automation:** GitHub Agent Library Manager auto-searches the manufacturing category in the AI-Agent-Templates repository, discovers all industry-specific agents (equipment_monitoring_agent, predictive_maintenance_agent, etc.), downloads and installs each one, auto-creates separate GUID-based groups for "Predictive Maintenance" and "Equipment Management", and enables the appropriate agents per group—zero manual organization or categorization work.

### 10. "Validate and optimize my entire AI infrastructure configuration"
- **Automation:** IQ Booster Agent auto-runs a comprehensive diagnostic: validates all Azure connections, checks model availability and performance quotas, optimizes deployment sizing (suggests cost-effective alternatives), identifies unused resources, confirms memory configurations are sufficient, updates performance parameters automatically, and provides a complete infrastructure audit report—zero manual infrastructure assessment needed.

---

## Key Automation Patterns

### Pattern 1: Discovery & Auto-Configuration (Prompts 1, 4, 6)
- **IQ Booster Agent** scans Azure resources automatically
- **Zero manual Azure portal work** - system finds everything
- **Auto-applies changes** to both local and cloud environments

### Pattern 2: Library Management & Installation (Prompts 2, 5, 9)
- **GitHub Agent Library Manager** discovers agents from public repository
- **Zero manual downloading** - system pulls directly from GitHub
- **Auto-registration** as callable functions with OpenAI integration

### Pattern 3: Workflow Orchestration & Execution (Prompts 3, 8, 10)
- **Workflow Runner Agent** reads JSON transcript format
- **Zero manual step execution** - system runs all steps with variable substitution
- **Auto-error handling** with conditional fallback logic

### Pattern 4: Cross-Agent Coordination (All Prompts)
- **Multiple agents work together** without user intervention
- **Zero manual agent-to-agent communication** - OpenAI routes appropriately
- **Auto-feedback loops** - outputs from one agent feed into the next

---

## Business Impact

| Manual Work | Auto-Automation Eliminates |
|------------|--------------------------|
| **Resource Discovery** | IQ Booster auto-scans subscriptions |
| **Azure Portal Navigation** | System finds all resources programmatically |
| **Configuration File Editing** | IQ Booster updates local + cloud configs automatically |
| **Agent Installation** | GitHub Library Manager downloads + installs in one call |
| **Deployment Scripts** | Workflow Runner executes JSON transcripts with variable substitution |
| **Testing & Validation** | Workflows include built-in test steps that capture outputs |
| **Infrastructure Audits** | IQ Booster runs diagnostic checks automatically |
| **Agent Lifecycle Management** | Library Manager handles versioning, groups, and access control |
| **Production Updates** | Configuration changes apply immediately without restarts |
| **Documentation Sync** | System auto-logs all changes to memory for audit trail |

---

## Technical Capabilities Demonstrated

### IQ Booster Agent Auto-Capabilities
- Discovers Azure OpenAI resources across subscriptions
- Lists available models without API documentation lookup
- Provisions new deployments without Azure portal
- Updates Azure Function App app settings (production environment)
- Modifies local.settings.json (development environment)
- Validates configurations end-to-end
- Suggests model optimizations based on quotas
- Auto-detects and fixes configuration mismatches

### Workflow Runner Agent Auto-Capabilities
- Parses JSON workflow transcripts
- Substitutes variables at runtime from multiple sources
- Executes multi-step sequences with output chaining
- Captures step outputs as variables for next steps
- Handles conditional logic (if/then/else)
- Implements error handling with on_error blocks
- Supports foreach loops for bulk operations
- Validates workflows before execution
- Performs dry-runs to preview changes

### GitHub Agent Library Manager Auto-Capabilities
- Discovers all 65+ agents in public repository
- Searches agents by keyword across name, description, features
- Filters agents by industry vertical/category
- Downloads agent code directly from GitHub raw URLs
- Installs agents to Azure File Storage (agents/ and multi_agents/ shares)
- Creates GUID-based agent groups for role-based access
- Manages agent versioning and updates
- Tracks installation history and dependencies

---

## Demo Flow Recommendations

**For Maximum Impact, Demonstrate in This Order:**

1. **Start with Discovery (Prompt 4)** - Show the system "seeing" all Azure resources without portal navigation
2. **Then Auto-Configuration (Prompt 1)** - Show upgrading the AI model automatically
3. **Add Library Management (Prompt 2)** - Show installing pre-built agents from GitHub
4. **Run a Workflow (Prompt 3)** - Show orchestration of complex multi-step processes
5. **End with Comprehensive Audit (Prompt 10)** - Show the system validating its own configuration

This progression demonstrates: **Discovery → Configuration → Integration → Orchestration → Validation**

---

## Key Messaging

> "Copilot Agent 365 automates the entire AI infrastructure lifecycle. Your agents discover resources, configure themselves, run workflows, and manage their own library of capabilities. What used to take hours of manual Azure portal clicks and script editing now happens in seconds."

**Zero Manual Configuration. Zero Manual Deployment. Zero Manual Infrastructure Management.**

