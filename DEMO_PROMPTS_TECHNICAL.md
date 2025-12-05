# Copilot Agent 365 - Technical Demo Prompts

## 10 Advanced Technical Prompts for Enterprise AI Audience

These prompts showcase the sophisticated technical architecture of Copilot Agent 365, demonstrating multi-agent orchestration, Azure integration, real-time resource management, and API capabilities.

---

## 1. "Execute an IQ Boost to automatically discover the best available GPT model in my Azure subscription and deploy it with single-command configuration to both local development and production Azure Function App"

**Why it's impressive:**
- **Multi-step Azure orchestration**: Demonstrates the IQBoosterAgent executing a complex workflow that spans Azure CLI operations, JSON transformation, and environment management
- **Live resource discovery**: Shows real-time querying of Azure OpenAI resources and model deployments using Azure CLI integration
- **Dual-environment synchronization**: Proves the system can atomically update both local.settings.json AND Azure Function App settings in production without manual intervention
- **Intelligent prioritization**: The agent implements a priority queue (GPT-5 > GPT-4o > GPT-4) to find the optimal model, showing decision-making logic embedded in the agent
- **Zero-downtime deployment**: Changes are applied live to the Azure Function, demonstrating serverless-aware infrastructure management

---

## 2. "Show me a detailed execution trace of how the system processes a user request: from HTTP entry point through agent selection, Azure OpenAI function calling, memory context retrieval, and finally response formatting with voice synthesis splitting"

**Why it's impressive:**
- **End-to-end request flow visibility**: Exposes the complete request-response lifecycle from the `businessinsightbot_function` HTTP trigger through the `Assistant` class orchestration
- **Function calling mechanics**: Demonstrates how Azure OpenAI's function calling API is used to dynamically invoke agents based on natural language understanding, not hardcoded routing
- **Multi-layer memory injection**: Shows the system's ability to inject shared memory + user-specific memory from Azure File Storage into the context window before each OpenAI call
- **Dual-response formatting**: Illustrates the sophisticated response splitting mechanism (using `|||VOICE|||` delimiter) that produces both formatted markdown and concise voice responses from a single model output
- **Architectural transparency**: Gives technical audiences insight into how stateless Azure Functions achieve stateful conversations through careful context management

---

## 3. "Create a custom workflow transcript that demonstrates variable substitution, conditional step execution, Azure CLI command chaining, JSON file mutations, and error handling—then execute it with dry-run mode to show exactly what would happen"

**Why it's impressive:**
- **Declarative infrastructure-as-code**: Shows how workflows are defined as JSON documents, enabling version control, peer review, and audit trails for infrastructure changes
- **Advanced variable substitution**: Demonstrates `${step_id.output_name}` references that create data dependency chains across workflow steps
- **Multi-action orchestration**: Illustrates support for diverse action types (az_command, update_json_file, template, evaluate, foreach) in a single workflow
- **Dry-run capability**: Proves the system can safely preview complex operations before execution, critical for production safety
- **Error handling patterns**: Shows on_error blocks, continue_on_error flags, and abort semantics, demonstrating enterprise-grade resilience patterns

---

## 4. "Configure the system to enable specific agents for a particular user GUID while filtering out others via agent_config, then demonstrate how the Agent Manager loads only authorized agents for that user's requests"

**Why it's impressive:**
- **Per-user agent authorization**: Implements role-based access control at the agent level, allowing administrators to grant/revoke agent capabilities per user or user group
- **Dynamic agent discovery and filtering**: Shows the agent loading pipeline in `load_agents_from_folder()` that respects per-user configuration stored in Azure File Storage
- **Fine-grained capability control**: Proves the system can selectively disable agents (e.g., restrict ManageMemoryAgent to prevent unauthorized memory tampering) without code changes
- **File-driven configuration**: Demonstrates configuration-as-code approach where agent permissions are stored in JSON files in Azure Storage, enabling GitOps workflows
- **Performance optimization**: Shows how agent filtering prevents unnecessary agent instantiation and OpenAI function schema registration for disabled agents

---

## 5. "Store a complex multi-fact memory entry using ManageMemoryAgent with memory_type, importance rating, and tags, then retrieve it using ContextMemoryAgent with keyword filtering across user-specific memory—demonstrating the dual-layer memory system"

**Why it's impressive:**
- **Dual-layer memory architecture**: Showcases the separation between shared memory (all users) and user-specific memory (per GUID), enabling both global knowledge bases and personalized context
- **Structured memory format**: Demonstrates how memories are stored with metadata (theme, importance, date, time) enabling rich query patterns
- **Memory recall with filtering**: Shows semantic search via keywords, allowing retrieval of contextually relevant memories rather than simple lookups
- **Metadata-driven queries**: Proves the system can filter memories by tags, importance ratings, and timestamps, enabling sophisticated context selection strategies
- **Persistent cross-session context**: Illustrates how memories stored in Azure File Storage survive Azure Function restarts and scale events, enabling true persistent context

---

## 6. "Execute the WorkflowRunner agent to load a complex workflow from the workflows/ directory, demonstrate variable interpolation across 7+ sequential steps, and show how step outputs feed into subsequent step inputs"

**Why it's impressive:**
- **Declarative workflow engine**: Shows that the system implements a full workflow execution runtime embedded in a single agent, enabling complex business logic without code deployment
- **Stateful step execution**: Demonstrates how the WorkflowRunner maintains execution context (`step_outputs` dictionary) across multiple asynchronous operations
- **Data flow between steps**: Illustrates JSON path expressions (`$.fieldname`) for extracting and passing data between steps, creating a composable pipeline architecture
- **Azure CLI integration**: Shows native Azure CLI command execution within workflows, enabling infrastructure automation without external tools
- **Error handling and continuation**: Demonstrates `continue_on_error` flags and conditional validation blocks, showing sophisticated error recovery in complex workflows

---

## 7. "Demonstrate how the system handles concurrent requests from multiple users with different GUIDs, showing how memory contexts are properly isolated and how the Azure Function scales horizontally to serve all requests simultaneously"

**Why it's impressive:**
- **True multi-tenancy within a single function**: Shows the system's ability to isolate memory contexts per user GUID without any cross-contamination, critical for enterprise deployments
- **Stateless function design**: Proves Azure Functions remain fully stateless while achieving stateful user experiences through storage layer abstraction
- **Horizontal scalability**: Demonstrates how the Consumption plan can auto-scale from 0 to 200+ instances without architectural changes, handling traffic spikes
- **Memory context switching**: Shows the dynamic memory context switching in `storage_manager.set_memory_context(user_guid)` that enables per-user personalization without per-user containers
- **Concurrent agent execution**: Illustrates how multiple agents can execute simultaneously across different user contexts, maximizing throughput

---

## 8. "Load custom agents from Azure File Storage shares (agents/ and multi_agents/ directories), dynamically generate OpenAI function schemas on startup, and show how the system routes user requests to appropriate agents via GPT's function_call mechanism"

**Why it's impressive:**
- **Dynamic agent marketplace**: Shows how agents uploaded to Azure File Storage are automatically discovered and loaded at function startup, enabling "hot-deploy" capabilities without recompiling
- **Automatic schema generation**: Demonstrates how agent metadata (name, description, parameters) is automatically extracted and converted to OpenAI-compatible function schemas
- **Dual-source agent loading**: Illustrates loading from both local `agents/` folder AND remote Azure File Storage, enabling version control while supporting runtime-deployed custom agents
- **Natural language routing**: Proves Azure OpenAI's function calling automatically selects the right agent based on user intent, not manual intent classification
- **Zero-knowledge deployment**: Shows that new agents can be deployed without the central system knowing about them beforehand—true plugin architecture

---

## 9. "Configure Power Automate integration to show how user context flows from Office 365 through the Power Automate enrichment layer, into the Azure Function, and how the system uses user profile information to personalize agent behavior"

**Why it's impressive:**
- **Enterprise identity integration**: Demonstrates end-to-end SSO flow from Teams/M365 Copilot through Power Automate to Azure Function, leveraging Entra ID for authentication
- **Context enrichment pipeline**: Shows how Power Automate captures user profile (name, email, department, job title) and injects it as `user_context` parameter to the function
- **User-aware agent behavior**: Illustrates how agents can access user profile data to customize responses, recommendations, and memory retrieval based on organizational context
- **Office 365 integration**: Proves the system can operate seamlessly within Microsoft 365 ecosystem, accessing Graph API data via Power Automate connectors
- **Enterprise compliance**: Demonstrates how user context enables audit trails (which user accessed what) required for SOC 2 and regulatory compliance

---

## 10. "Show how the system persists memories to Azure File Storage across multiple function invocations, survives Azure Function cold starts and scale events, and maintains conversation context in the face of infrastructure failures—demonstrating true resilience"

**Why it's impressive:**
- **Persistent distributed memory**: Shows how memories written to Azure File Storage (`memory/users/{guid}_context.txt`) survive Azure Function restarts, scale events, and container recycling
- **Infrastructure-agnostic state management**: Demonstrates the system architecture is resilient to underlying Azure infrastructure changes—function can restart, scale to multiple instances, or move between regions without losing context
- **Cold start recovery**: Proves that even after a complete function cold start (which can take 3+ seconds), the system immediately reloads full memory context from Azure Storage
- **Consistency guarantees**: Illustrates how shared memory (`memory/shared/`) and user memory (`memory/users/`) are kept consistent across concurrent requests
- **Cost optimization**: Shows how memory is stored in cheap Azure File Storage ($5-10/month) rather than more expensive caching layers, enabling enterprise-scale personalization economically
- **Scalability without limits**: Demonstrates that the per-user memory isolation model enables unlimited concurrent users without memory contention or synchronization overhead

---

## Bonus: Advanced Integration Scenarios

### Scenario A: Multi-Agent Orchestration
"Create an orchestrator agent that coordinates multiple specialized agents: ContextMemoryAgent retrieves user history, a custom NLP agent extracts entities from the user's input, ManageMemoryAgent stores new insights, and a response-formatting agent produces final output—all within a single request/response cycle"

**Why it's impressive:**
- Shows agent-to-agent communication patterns without direct coupling
- Demonstrates pipeline composition where output from one agent becomes input to another
- Proves the system scales to complex multi-agent workflows within function's token budget

### Scenario B: Real-Time Resource Optimization
"Execute a workflow that monitors Azure Function App performance metrics via Application Insights, automatically scales the Function App plan based on load, and adjusts memory allocation—demonstrating autonomous infrastructure optimization"

**Why it's impressive:**
- Shows the system can read operational metrics and adjust infrastructure in response
- Demonstrates closed-loop optimization without human intervention
- Proves cost optimization capabilities (scaling down during low traffic)

### Scenario C: Memory Analytics
"Query all stored memories across the system, aggregate statistics by memory type and user GUID, generate insights about conversation patterns, and produce a dashboard-ready JSON report—demonstrating data analytics capabilities on stored context"

**Why it's impressive:**
- Shows memories are queryable at scale, enabling organizational insights
- Demonstrates the system can surface hidden patterns in conversation data
- Proves value of persistent memory beyond individual conversations

---

## Technical Audience Engagement Strategy

When presenting these prompts:

1. **Start with #10** - Show the foundation (resilience + persistence)
2. **Move to #2** - Reveal the request-response architecture
3. **Jump to #4** - Demonstrate security/authorization
4. **Showcase #1** - Wow with automation capabilities
5. **Deep-dive #3, #6** - Prove workflow sophistication
6. **Finish with #7, #8** - Illustrate scalability

This order builds from "how does it work" → "how is it secure" → "how does it scale" → "what can it do", matching how technical architects evaluate systems.

---

## Key Technical Themes These Prompts Highlight

| Theme | Prompts | Value |
|-------|---------|-------|
| **Multi-Agent Orchestration** | #1, #3, #6, #8 | Shows modular AI without monolithic models |
| **Azure Integration** | #1, #4, #7, #9 | Proves deep M365/Azure ecosystem integration |
| **Real-time Resource Management** | #1, #7, Scenario B | Demonstrates autonomous optimization |
| **Persistent Memory Architecture** | #5, #10 | Shows true stateful AI without centralized databases |
| **Security & Authorization** | #4, #9 | Addresses enterprise compliance concerns |
| **Scalability** | #7, #8, #10 | Proves serverless-native design |
| **Infrastructure-as-Code** | #3, #6 | Enables version control and audit trails |
| **Enterprise Features** | #9, #10 | Connects to existing M365 workflows |

---

**Generated for Copilot Agent 365 - Enterprise AI Assistant Platform**

*These prompts are designed to be executed in sequence during technical demonstrations or submitted individually to focused evaluation audiences.*
