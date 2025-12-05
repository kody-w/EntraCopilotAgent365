# Copilot Agent 365 - Demo Prompts Index

This directory contains comprehensive demo prompts showcasing Copilot Agent 365's automation and self-management capabilities.

## Files Included

### 1. DEMO_PROMPTS.md (Primary Document)
**Full detailed demo prompts with complete explanations**
- 10 automation-focused demo prompts
- Detailed automation descriptions for each prompt
- Key automation patterns and analysis
- Business impact table
- Technical capabilities breakdown
- Recommended demo flow sequence
- Key messaging guidelines

### 2. DEMO_PROMPTS_SUMMARY.txt (Quick Reference)
**One-page executive summary of all prompts**
- Quick summary of each prompt
- Key automation patterns
- Business impact overview
- Recommended demo sequence
- Core agent capabilities
- File locations and messaging

### 3. This File (DEMO_PROMPTS_INDEX.md)
**Navigation and structure guide**

---

## Quick Access to Demo Prompts

### Discovery & Configuration Demos (IQ Booster Agent)

**Prompt 1:** "Boost my AI to the latest model"
- Discovers Azure OpenAI resources
- Identifies best available model
- Automatically deploys new model
- Updates local and cloud configurations

**Prompt 4:** "Discover what Azure OpenAI resources I have and what models are available"
- Auto-scans entire Azure subscription
- Lists resources with locations and SKUs
- Shows available model types and deployments
- Displays quotas and recommendations

**Prompt 6:** "Check my current AI configuration and fix any issues automatically"
- Validates all configurations
- Fixes mismatches and stale settings
- Reports all changes made

**Prompt 7:** "Update all my configuration values to use the new Azure endpoint"
- Discovers new endpoints
- Updates production and development environments
- Restarts function app automatically

### Agent Library Management (GitHub Agent Library Manager)

**Prompt 2:** "Set up my agent library with sales team capabilities"
- Discovers 65+ agent repository
- Searches for sales-specific agents
- Downloads and installs to Azure Storage
- Creates GUID-based agent groups

**Prompt 5:** "Install a custom email agent and enable it just for my team"
- Finds specific agent from repository
- Downloads Python code from GitHub
- Installs to Azure File Storage
- Creates user group with access control

**Prompt 9:** "Install all agents from the manufacturing vertical and organize them by category"
- Searches industry-specific agents
- Downloads all agents in category
- Auto-creates organized GUID-based groups
- Enables appropriate agents per group

### Workflow Orchestration (Workflow Runner Agent)

**Prompt 3:** "Run our deployment workflow automatically"
- Loads JSON workflow transcript
- Auto-substitutes all variables
- Executes steps in sequence
- Captures outputs for next steps
- Handles errors with fallback actions

**Prompt 8:** "Run a workflow to deploy my latest agents and test them"
- Discovers agents in local folders
- Executes multi-step deployment
- Runs integration tests with mock requests
- Captures test results in variables
- Triggers on_complete or on_error actions

### Comprehensive Automation

**Prompt 10:** "Validate and optimize my entire AI infrastructure configuration"
- Runs comprehensive diagnostic
- Validates all Azure connections
- Checks model availability and quotas
- Suggests cost optimizations
- Updates performance parameters automatically
- Provides complete infrastructure audit

---

## Key Concepts

### Zero Manual Work Principle

Every prompt demonstrates the elimination of manual work:

- **Zero Azure Portal Navigation** - System discovers resources programmatically
- **Zero Configuration File Editing** - IQ Booster updates files automatically
- **Zero Manual Agent Installation** - Library Manager downloads and installs
- **Zero Script Execution** - Workflow Runner executes orchestrated steps
- **Zero Testing** - Workflows include built-in test steps with error handling
- **Zero Verification** - IQ Booster validates everything automatically

### Three Core Agents Working Together

1. **IQ Booster Agent** - Infrastructure discovery and configuration
2. **Workflow Runner Agent** - Multi-step process orchestration
3. **GitHub Agent Library Manager** - Agent lifecycle management

These agents orchestrate via Azure OpenAI function calling, creating a self-managing system.

---

## Automation Patterns

### Pattern 1: Auto-Discovery
System finds resources without human navigation
- Discovers Azure OpenAI resources
- Lists available models
- Identifies configuration issues
- Scans for unused resources

### Pattern 2: Auto-Configuration
System applies changes across environments
- Updates local.settings.json
- Modifies Azure Function App settings
- Deploys new resources
- Fixes configuration mismatches

### Pattern 3: Auto-Installation
System downloads and integrates capabilities
- Finds agents in public repository
- Downloads from GitHub
- Installs to Azure File Storage
- Registers as callable functions

### Pattern 4: Auto-Orchestration
System runs multi-step workflows
- Reads JSON workflow definitions
- Substitutes variables at runtime
- Chains steps with output capture
- Handles errors with fallback logic

### Pattern 5: Auto-Validation
System checks itself and fixes issues
- Validates configurations end-to-end
- Detects and fixes mismatches
- Suggests optimizations
- Provides audit reports

---

## Recommended Demo Sequence

For maximum impact, demonstrate in this order:

1. **Discovery (Prompt 4)** - 3 minutes
   - Show system "seeing" all Azure resources
   - No Azure portal needed
   - Visual impact: System knows your infrastructure

2. **Auto-Configuration (Prompt 1)** - 4 minutes
   - Show automatic model upgrade
   - Watch local + cloud configs update
   - Visual impact: Production changes instantly applied

3. **Library Management (Prompt 2)** - 5 minutes
   - Show agent discovery in public repo
   - Watch agents download and install
   - Visual impact: Capabilities added with one prompt

4. **Workflow Execution (Prompt 3)** - 5 minutes
   - Show JSON workflow reading
   - Watch multi-step execution with variable chaining
   - Visual impact: Complex automation without scripts

5. **Comprehensive Audit (Prompt 10)** - 4 minutes
   - Show full infrastructure validation
   - Watch suggestions and automatic fixes
   - Visual impact: Self-optimizing system

**Total Demo Time: 20-25 minutes**

---

## Technical Stack Demonstrated

- **Azure OpenAI** - GPT-4o for intelligent routing
- **Azure Functions** - Serverless execution runtime
- **Azure File Storage** - Persistent memory and agent storage
- **GitHub** - Public agent repository (65+ agents)
- **Azure CLI** - Programmatic resource management
- **JSON** - Workflow transcript format
- **Python** - Agent execution engine
- **Power Automate** - Optional enterprise integration

---

## Key Messaging

### Primary Message
"Copilot Agent 365 automates the entire AI infrastructure lifecycle. Your agents discover resources, configure themselves, run workflows, and manage their own library of capabilities. What used to take hours of manual Azure portal clicks and script editing now happens in seconds."

### Key Tagline
**Zero Manual Configuration. Zero Manual Deployment. Zero Manual Infrastructure Management.**

### Supporting Messages

- "Your infrastructure discovers itself"
- "Configuration changes apply instantly"
- "Workflows execute with full intelligence"
- "Agent library self-organizes"
- "System validates and optimizes itself"

---

## File Locations

All files are in the project root directory:

```
/Users/kodywildfeuer/Documents/RappAI/EntraCopilotAgent365/
├── DEMO_PROMPTS.md                    # Full detailed prompts (PRIMARY)
├── DEMO_PROMPTS_SUMMARY.txt           # Quick reference
├── DEMO_PROMPTS_INDEX.md              # This file
└── DEMO_PROMPTS_TECHNICAL.md          # (Optional) Technical deep-dive
```

---

## How to Use These Materials

### For Sales/Marketing Demos
- Use DEMO_PROMPTS_SUMMARY.txt for quick talking points
- Follow the recommended demo sequence
- Emphasize "zero manual work" messaging
- Show 20-25 minute live demonstration

### For Product Documentation
- Reference DEMO_PROMPTS.md for detailed capabilities
- Link to prompt examples in your documentation
- Use automation patterns to explain features
- Highlight business impact of each agent

### For Development/Engineering
- Study technical capabilities of each agent
- Understand automation patterns and flow
- Build custom agents following these patterns
- Reference as examples for new features

### For Training
- Use prompts as hands-on lab exercises
- Follow demo sequence as learning path
- Practice each agent's capabilities
- Build confidence with progressive complexity

---

## Next Steps

1. **Read** DEMO_PROMPTS_SUMMARY.txt for quick overview (5 minutes)
2. **Review** DEMO_PROMPTS.md for detailed explanations (15 minutes)
3. **Plan** your demo using the recommended sequence
4. **Execute** a 20-25 minute demonstration
5. **Customize** prompts for your specific use cases

---

Generated: December 4, 2025  
Strategy: Automation & Self-Management  
Focus: Zero Manual Work  
Total Prompts: 10  
Coverage: 3 Core Agents + Cross-Agent Orchestration  

