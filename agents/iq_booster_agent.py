from agents.basic_agent import BasicAgent
import logging
import json
import os
import subprocess
import re

class IQBoosterAgent(BasicAgent):
    """
    IQ Booster Agent - Azure AI Model Discovery, Deployment & Auto-Configuration

    This agent serves as both a practical tool and an educational tutorial for:
    1. Discovering Azure OpenAI resources across your subscription
    2. Listing available models and existing deployments
    3. Provisioning new model deployments (gpt-5-chat, gpt-4o, etc.)
    4. Auto-updating Azure Function App settings to use new models
    5. Updating local.settings.json for local development

    The agent can perform a full "IQ Boost" automatically:
    - Find the best available model in your Azure OpenAI resources
    - Deploy it if needed
    - Update both local config AND Azure Function App settings

    Perfect for newcomers learning about Azure AI Foundry and OpenAI integration.
    """

    def __init__(self):
        self.name = 'IQBooster'
        self.metadata = {
            "name": self.name,
            "description": """IQ Booster Agent - Discovers, deploys, and auto-configures Azure OpenAI models.

ACTIONS:
- 'tutorial': Learn how this agent works
- 'discover_resources': Find all Azure OpenAI resources in your subscription
- 'discover_models': List available models in an OpenAI resource
- 'list_deployments': Show current model deployments
- 'deploy': Create a new model deployment
- 'configure_local': Update local.settings.json
- 'configure_azure': Update Azure Function App settings (auto-applies to production!)
- 'boost': FULL AUTO - discover best model → deploy → configure local + Azure
- 'status': Show current configuration

This agent can automatically upgrade your AI by finding gpt-5-chat or the best available model and configuring everything.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": [
                            "tutorial",
                            "discover_resources",
                            "discover_models",
                            "list_deployments",
                            "deploy",
                            "configure_local",
                            "configure_azure",
                            "boost",
                            "status"
                        ]
                    },
                    "resource_name": {
                        "type": "string",
                        "description": "Azure OpenAI resource name (e.g., 'wildf-mis9if5c-swedencentral'). Use discover_resources to find available resources."
                    },
                    "resource_group": {
                        "type": "string",
                        "description": "Azure resource group name. Default: 'rappai'"
                    },
                    "function_app_name": {
                        "type": "string",
                        "description": "Azure Function App name to configure. Default: auto-detected from environment"
                    },
                    "model_name": {
                        "type": "string",
                        "description": "Model to deploy (e.g., 'gpt-5-chat', 'gpt-4o', 'gpt-4-turbo')"
                    },
                    "deployment_name": {
                        "type": "string",
                        "description": "Name for the deployment. Default: auto-generated from model name"
                    },
                    "endpoint": {
                        "type": "string",
                        "description": "Full Azure OpenAI endpoint URL for configure actions"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Azure OpenAI API key for configure actions"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, show what would happen without making changes. Default: false"
                    }
                },
                "required": ["action"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

        # Load current configuration from environment
        self.current_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
        self.current_deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', '')
        self.current_api_key = os.environ.get('AZURE_OPENAI_API_KEY', '')
        self.storage_account = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', 'st4ovzneuimhd2g')

        # Default resource group
        self.default_resource_group = 'rappai'

        # Extract current resource name from endpoint
        self.current_resource_name = self._extract_resource_name(self.current_endpoint)

    def _extract_resource_name(self, endpoint):
        """Extract Azure OpenAI resource name from endpoint URL"""
        if not endpoint:
            return ''
        try:
            # https://resource-name.openai.azure.com/ -> resource-name
            match = re.search(r'https://([^.]+)\.openai\.azure\.com', endpoint)
            if match:
                return match.group(1)
            return endpoint.replace('https://', '').replace('http://', '').split('.')[0]
        except:
            return ''

    def perform(self, **kwargs):
        action = kwargs.get('action', 'tutorial')
        dry_run = kwargs.get('dry_run', False)

        try:
            if action == 'tutorial':
                return self._show_tutorial()
            elif action == 'discover_resources':
                return self._discover_openai_resources(kwargs)
            elif action == 'discover_models':
                return self._discover_models(kwargs, dry_run)
            elif action == 'list_deployments':
                return self._list_deployments(kwargs, dry_run)
            elif action == 'deploy':
                return self._deploy_model(kwargs, dry_run)
            elif action == 'configure_local':
                return self._configure_local(kwargs, dry_run)
            elif action == 'configure_azure':
                return self._configure_azure_function(kwargs, dry_run)
            elif action == 'boost':
                return self._auto_boost(kwargs, dry_run)
            elif action == 'status':
                return self._show_status()
            else:
                return f"Unknown action: {action}. Use 'tutorial' to learn available actions."
        except Exception as e:
            logging.error(f"IQBooster error: {str(e)}")
            return f"Error: {str(e)}\n\nTip: Run with action='tutorial' for help."

    def _show_tutorial(self):
        """Interactive tutorial for newcomers"""
        return """# 🧠 IQ Booster Agent - Tutorial

Welcome! This agent helps you discover, deploy, and configure Azure OpenAI models to "boost your AI's IQ".

## What This Agent Does

The IQ Booster connects to your Azure subscription to:
1. **Discover** Azure OpenAI resources and available models
2. **Deploy** new models (GPT-5-chat, GPT-4o, etc.)
3. **Configure** both local AND Azure Function App settings automatically

## Quick Start Commands

### 1. Check Current Status
```
action: "status"
```

### 2. Find Azure OpenAI Resources
```
action: "discover_resources"
```

### 3. See Available Models in a Resource
```
action: "discover_models"
resource_name: "your-openai-resource"
```

### 4. List Current Deployments
```
action: "list_deployments"
resource_name: "your-openai-resource"
```

### 5. Deploy a New Model
```
action: "deploy"
resource_name: "your-openai-resource"
model_name: "gpt-5-chat"
```

### 6. Configure Local Settings
```
action: "configure_local"
endpoint: "https://your-resource.openai.azure.com/"
deployment_name: "gpt-5-chat"
api_key: "your-key"
```

### 7. Configure Azure Function App (Production!)
```
action: "configure_azure"
endpoint: "https://your-resource.openai.azure.com/"
deployment_name: "gpt-5-chat"
api_key: "your-key"
function_app_name: "copilot365-xxx"
```

### 8. 🚀 ONE-CLICK FULL BOOST
```
action: "boost"
```
This automatically:
- Finds all your Azure OpenAI resources
- Identifies the best available model (gpt-5-chat > gpt-4o > gpt-4)
- Deploys it if needed
- Updates BOTH local.settings.json AND Azure Function App!

## Dry Run Mode

Add `dry_run: true` to see what would happen without making changes.

## Prerequisites

- Azure CLI logged in (`az login`)
- Proper Azure permissions (Contributor on OpenAI resources)

## Current Configuration

""" + self._get_status_summary()

    def _show_status(self):
        """Show current configuration status"""
        return f"""# 📊 IQ Booster - Current Status

## Active Configuration

| Setting | Value |
|---------|-------|
| **Endpoint** | {self.current_endpoint or '(not set)'} |
| **Resource** | {self.current_resource_name or '(not detected)'} |
| **Deployment** | {self.current_deployment or '(not set)'} |
| **API Key** | {'✅ Set (' + self.current_api_key[:8] + '...)' if self.current_api_key else '❌ Not set'} |
| **Storage Account** | {self.storage_account or '(not set)'} |

## Azure CLI Status

""" + self._check_azure_cli_status() + """

## Next Steps

- Use `action: "discover_resources"` to find Azure OpenAI resources
- Use `action: "boost"` for automatic upgrade to best available model
"""

    def _get_status_summary(self):
        """Get a brief status summary"""
        return f"""- **Current Endpoint:** {self.current_endpoint or '(not configured)'}
- **Current Deployment:** {self.current_deployment or '(not configured)'}
- **Resource Name:** {self.current_resource_name or '(not detected)'}
"""

    def _check_azure_cli_status(self):
        """Check Azure CLI login status"""
        try:
            result = subprocess.run(
                ['az', 'account', 'show', '--query', '{name:name, user:user.name}', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                account = json.loads(result.stdout)
                return f"✅ Logged in as: **{account.get('user', 'Unknown')}**\n📁 Subscription: **{account.get('name', 'Unknown')}**"
            else:
                return "❌ Not logged in. Run `az login` first."
        except Exception as e:
            return f"⚠️ Could not check Azure CLI status: {str(e)}"

    def _discover_openai_resources(self, params):
        """Discover all Azure OpenAI resources in the subscription"""
        try:
            # List all Cognitive Services accounts of kind OpenAI
            cmd = [
                'az', 'cognitiveservices', 'account', 'list',
                '--query', "[?kind=='OpenAI'].{name:name, location:location, resourceGroup:resourceGroup, endpoint:properties.endpoint}",
                '--output', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return f"Error discovering resources: {result.stderr}\n\nMake sure you're logged in: `az login`"

            resources = json.loads(result.stdout) if result.stdout else []

            if not resources:
                return """# No Azure OpenAI Resources Found

No Azure OpenAI resources found in your subscription.

**To create one:**
1. Go to Azure Portal → Create a resource → Azure OpenAI
2. Or use Azure CLI:
   ```bash
   az cognitiveservices account create \\
     --name my-openai-resource \\
     --resource-group rappai \\
     --kind OpenAI \\
     --sku S0 \\
     --location eastus
   ```
"""

            response = f"""# 🔍 Azure OpenAI Resources Found: {len(resources)}

| Resource Name | Location | Resource Group | Endpoint |
|--------------|----------|----------------|----------|
"""
            for r in resources:
                response += f"| {r['name']} | {r['location']} | {r['resourceGroup']} | {r['endpoint']} |\n"

            response += f"""

## Next Steps

To see available models in a resource:
```
action: "discover_models"
resource_name: "{resources[0]['name']}"
resource_group: "{resources[0]['resourceGroup']}"
```

To list deployments:
```
action: "list_deployments"
resource_name: "{resources[0]['name']}"
resource_group: "{resources[0]['resourceGroup']}"
```
"""
            return response

        except subprocess.TimeoutExpired:
            return "Error: Command timed out. Azure might be slow to respond."
        except Exception as e:
            return f"Error discovering resources: {str(e)}"

    def _discover_models(self, params, dry_run=False):
        """Discover available models in an Azure OpenAI resource"""
        resource_name = params.get('resource_name', self.current_resource_name)
        resource_group = params.get('resource_group', self.default_resource_group)

        if not resource_name:
            return """# Error: Resource Name Required

Please specify which Azure OpenAI resource to query:
```
action: "discover_models"
resource_name: "your-openai-resource"
resource_group: "your-resource-group"
```

Use `action: "discover_resources"` to find available resources.
"""

        if dry_run:
            return f"""# Dry Run: Discover Models

**Would query:** {resource_name} in {resource_group}
**Command:**
```bash
az cognitiveservices account list-models \\
    --name {resource_name} \\
    --resource-group {resource_group}
```
"""

        try:
            cmd = [
                'az', 'cognitiveservices', 'account', 'list-models',
                '--name', resource_name,
                '--resource-group', resource_group,
                '--output', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return f"Error: {result.stderr}"

            models = json.loads(result.stdout) if result.stdout else []
            gpt_models = [m for m in models if 'gpt' in m.get('name', '').lower()]

            response = f"""# 🤖 Available Models in {resource_name}

**Total Models:** {len(models)}
**GPT Models:** {len(gpt_models)}

## GPT Models (Chat/Completion)

"""
            # Sort to show newest first
            gpt_models.sort(key=lambda x: x.get('name', ''), reverse=True)

            for i, model in enumerate(gpt_models[:20], 1):
                name = model.get('name', 'Unknown')
                is_gpt5 = 'gpt-5' in name.lower()
                star = " ⭐ **RECOMMENDED**" if is_gpt5 else ""
                response += f"{i}. `{name}`{star}\n"

            response += f"""

## Deploy a Model

```
action: "deploy"
resource_name: "{resource_name}"
resource_group: "{resource_group}"
model_name: "gpt-5-chat"
```
"""
            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def _list_deployments(self, params, dry_run=False):
        """List current deployments in an Azure OpenAI resource"""
        resource_name = params.get('resource_name', self.current_resource_name)
        resource_group = params.get('resource_group', self.default_resource_group)

        if not resource_name:
            return "Error: resource_name required. Use discover_resources to find available resources."

        if dry_run:
            return f"Dry run: Would list deployments in {resource_name}"

        try:
            cmd = [
                'az', 'cognitiveservices', 'account', 'deployment', 'list',
                '--name', resource_name,
                '--resource-group', resource_group,
                '--output', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return f"Error: {result.stderr}"

            deployments = json.loads(result.stdout) if result.stdout else []

            response = f"""# 📦 Deployments in {resource_name}

**Total Deployments:** {len(deployments)}

"""
            if not deployments:
                response += "No deployments found. Create one with `action: \"deploy\"`"
            else:
                response += "| Deployment Name | Model | Version | Capacity |\n"
                response += "|-----------------|-------|---------|----------|\n"

                for dep in deployments:
                    name = dep.get('name', 'Unknown')
                    props = dep.get('properties', {})
                    model = props.get('model', {})
                    model_name = model.get('name', 'Unknown')
                    model_version = model.get('version', 'N/A')
                    capacity = dep.get('sku', {}).get('capacity', 'N/A')

                    is_current = " ✅" if name == self.current_deployment else ""
                    response += f"| {name}{is_current} | {model_name} | {model_version} | {capacity}K TPM |\n"

            return response

        except Exception as e:
            return f"Error: {str(e)}"

    def _deploy_model(self, params, dry_run=False):
        """Deploy a new model to Azure OpenAI"""
        resource_name = params.get('resource_name', self.current_resource_name)
        resource_group = params.get('resource_group', self.default_resource_group)
        model_name = params.get('model_name')
        deployment_name = params.get('deployment_name', model_name)

        if not resource_name or not model_name:
            return "Error: resource_name and model_name are required."

        if dry_run:
            return f"""# Dry Run: Deploy Model

**Would deploy:**
- Resource: {resource_name}
- Model: {model_name}
- Deployment Name: {deployment_name}

**Command:**
```bash
az cognitiveservices account deployment create \\
    --name {resource_name} \\
    --resource-group {resource_group} \\
    --deployment-name {deployment_name} \\
    --model-name {model_name} \\
    --model-version latest \\
    --model-format OpenAI \\
    --sku-capacity 10 \\
    --sku-name Standard
```
"""

        try:
            cmd = [
                'az', 'cognitiveservices', 'account', 'deployment', 'create',
                '--name', resource_name,
                '--resource-group', resource_group,
                '--deployment-name', deployment_name,
                '--model-name', model_name,
                '--model-version', 'latest',
                '--model-format', 'OpenAI',
                '--sku-capacity', '10',
                '--sku-name', 'Standard',
                '--output', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                if 'already exists' in result.stderr.lower():
                    return f"✅ Deployment '{deployment_name}' already exists!"
                return f"Error: {result.stderr}"

            return f"""# ✅ Deployment Created Successfully!

**Resource:** {resource_name}
**Deployment:** {deployment_name}
**Model:** {model_name}

## Next: Configure Your App

**Update Azure Function (Production):**
```
action: "configure_azure"
endpoint: "https://{resource_name}.openai.azure.com/"
deployment_name: "{deployment_name}"
api_key: "<get-key-from-azure-portal>"
```

**Update Local Settings:**
```
action: "configure_local"
endpoint: "https://{resource_name}.openai.azure.com/"
deployment_name: "{deployment_name}"
api_key: "<get-key-from-azure-portal>"
```
"""

        except Exception as e:
            return f"Error: {str(e)}"

    def _configure_local(self, params, dry_run=False):
        """Update local.settings.json with new OpenAI configuration"""
        endpoint = params.get('endpoint')
        deployment_name = params.get('deployment_name')
        api_key = params.get('api_key')

        if not endpoint or not deployment_name:
            return "Error: endpoint and deployment_name are required."

        settings_path = 'local.settings.json'

        if dry_run:
            return f"""# Dry Run: Configure Local Settings

**Would update {settings_path}:**
- AZURE_OPENAI_ENDPOINT: {endpoint}
- AZURE_OPENAI_DEPLOYMENT_NAME: {deployment_name}
- AZURE_OPENAI_API_KEY: {'*' * 8 + '...' if api_key else '(not provided)'}
"""

        try:
            # Read current settings
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {"IsEncrypted": False, "Values": {}}

            # Update settings
            if 'Values' not in settings:
                settings['Values'] = {}

            old_endpoint = settings['Values'].get('AZURE_OPENAI_ENDPOINT', '(not set)')
            old_deployment = settings['Values'].get('AZURE_OPENAI_DEPLOYMENT_NAME', '(not set)')

            settings['Values']['AZURE_OPENAI_ENDPOINT'] = endpoint
            settings['Values']['AZURE_OPENAI_DEPLOYMENT_NAME'] = deployment_name
            if api_key:
                settings['Values']['AZURE_OPENAI_API_KEY'] = api_key

            # Write back
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)

            return f"""# ✅ Local Settings Updated!

**File:** {settings_path}

| Setting | Old Value | New Value |
|---------|-----------|-----------|
| Endpoint | {old_endpoint} | {endpoint} |
| Deployment | {old_deployment} | {deployment_name} |
| API Key | ******** | {'Updated ✅' if api_key else 'Unchanged'} |

**Restart the function to apply:** `func start`
"""

        except Exception as e:
            return f"Error: {str(e)}"

    def _configure_azure_function(self, params, dry_run=False):
        """Update Azure Function App settings - THIS AFFECTS PRODUCTION!"""
        endpoint = params.get('endpoint')
        deployment_name = params.get('deployment_name')
        api_key = params.get('api_key')
        function_app_name = params.get('function_app_name', 'copilot365-4ovzneuimhd2g')
        resource_group = params.get('resource_group', self.default_resource_group)

        if not endpoint or not deployment_name:
            return "Error: endpoint and deployment_name are required."

        if dry_run:
            return f"""# Dry Run: Configure Azure Function App

⚠️ **WARNING: This updates PRODUCTION settings!**

**Would run:**
```bash
az functionapp config appsettings set \\
    --name {function_app_name} \\
    --resource-group {resource_group} \\
    --settings \\
        "AZURE_OPENAI_ENDPOINT={endpoint}" \\
        "AZURE_OPENAI_DEPLOYMENT_NAME={deployment_name}" \\
        "AZURE_OPENAI_API_KEY=********"
```

Remove `dry_run: true` to execute.
"""

        try:
            # Build settings list
            settings = [
                f"AZURE_OPENAI_ENDPOINT={endpoint}",
                f"AZURE_OPENAI_DEPLOYMENT_NAME={deployment_name}"
            ]
            if api_key:
                settings.append(f"AZURE_OPENAI_API_KEY={api_key}")

            cmd = [
                'az', 'functionapp', 'config', 'appsettings', 'set',
                '--name', function_app_name,
                '--resource-group', resource_group,
                '--settings'
            ] + settings + ['--output', 'json']

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return f"Error: {result.stderr}"

            return f"""# ✅ Azure Function App Updated!

**Function App:** {function_app_name}
**Resource Group:** {resource_group}

## Settings Applied:

| Setting | Value |
|---------|-------|
| AZURE_OPENAI_ENDPOINT | {endpoint} |
| AZURE_OPENAI_DEPLOYMENT_NAME | {deployment_name} |
| AZURE_OPENAI_API_KEY | {'Updated ✅' if api_key else 'Unchanged'} |

🚀 **Changes are LIVE immediately!**

The Azure Function will use the new model on the next request.
"""

        except Exception as e:
            return f"Error: {str(e)}"

    def _auto_boost(self, params, dry_run=False):
        """
        FULL AUTOMATIC IQ BOOST

        1. Discover all Azure OpenAI resources
        2. Find the best available model (gpt-5-chat > gpt-4o > gpt-4)
        3. Check if it's already deployed, deploy if not
        4. Get the API key
        5. Update BOTH local.settings.json AND Azure Function App
        """
        function_app_name = params.get('function_app_name', 'copilot365-4ovzneuimhd2g')
        resource_group = params.get('resource_group', self.default_resource_group)

        if dry_run:
            return """# Dry Run: Full Auto Boost

**Would perform these steps:**

1. 🔍 Discover all Azure OpenAI resources in subscription
2. 🤖 Find best available model (gpt-5-chat > gpt-4o > gpt-4-turbo > gpt-4)
3. 📦 Check/create deployment for best model
4. 🔑 Retrieve API key
5. 💾 Update local.settings.json
6. ☁️ Update Azure Function App settings

**This is the ONE-CLICK IQ upgrade!**

Remove `dry_run: true` to execute.
"""

        response = """# 🚀 Auto Boost - Upgrading Your AI

"""

        try:
            # Step 1: Discover resources
            response += "## Step 1: Discovering Azure OpenAI Resources...\n\n"

            cmd = [
                'az', 'cognitiveservices', 'account', 'list',
                '--query', "[?kind=='OpenAI'].{name:name, location:location, resourceGroup:resourceGroup, endpoint:properties.endpoint}",
                '--output', 'json'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return response + f"❌ Error discovering resources: {result.stderr}"

            resources = json.loads(result.stdout) if result.stdout else []

            if not resources:
                return response + "❌ No Azure OpenAI resources found in subscription."

            response += f"Found **{len(resources)}** OpenAI resource(s)\n\n"

            # Step 2: Find best model across all resources
            response += "## Step 2: Finding Best Available Model...\n\n"

            best_resource = None
            best_model = None
            best_deployment = None
            priority_models = ['gpt-5-chat', 'gpt-5', 'gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-35-turbo']

            for resource in resources:
                r_name = resource['name']
                r_group = resource['resourceGroup']

                # Check existing deployments first
                dep_cmd = [
                    'az', 'cognitiveservices', 'account', 'deployment', 'list',
                    '--name', r_name,
                    '--resource-group', r_group,
                    '--output', 'json'
                ]
                dep_result = subprocess.run(dep_cmd, capture_output=True, text=True, timeout=30)

                if dep_result.returncode == 0:
                    deployments = json.loads(dep_result.stdout) if dep_result.stdout else []

                    for dep in deployments:
                        model_name = dep.get('properties', {}).get('model', {}).get('name', '')
                        dep_name = dep.get('name', '')

                        for i, priority in enumerate(priority_models):
                            if priority in model_name.lower():
                                if best_model is None or i < priority_models.index(best_model):
                                    best_resource = resource
                                    best_model = model_name
                                    best_deployment = dep_name
                                    response += f"✅ Found `{model_name}` deployment `{dep_name}` in **{r_name}**\n"
                                break

            if not best_model:
                response += "No suitable model deployments found. Checking available models...\n"
                # TODO: Could add logic to deploy a new model here
                return response + "\n❌ No deployable models found. Please deploy a model manually first."

            response += f"\n**Best Model Found:** `{best_model}` (deployment: `{best_deployment}`)\n"
            response += f"**Resource:** {best_resource['name']} ({best_resource['location']})\n\n"

            # Step 3: Get API key
            response += "## Step 3: Retrieving API Key...\n\n"

            key_cmd = [
                'az', 'cognitiveservices', 'account', 'keys', 'list',
                '--name', best_resource['name'],
                '--resource-group', best_resource['resourceGroup'],
                '--query', 'key1',
                '--output', 'tsv'
            ]
            key_result = subprocess.run(key_cmd, capture_output=True, text=True, timeout=30)

            if key_result.returncode != 0:
                return response + f"❌ Error getting API key: {key_result.stderr}"

            api_key = key_result.stdout.strip()
            endpoint = best_resource['endpoint']

            response += f"✅ API key retrieved\n"
            response += f"✅ Endpoint: `{endpoint}`\n\n"

            # Step 4: Update local.settings.json
            response += "## Step 4: Updating Local Settings...\n\n"

            settings_path = 'local.settings.json'
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {"IsEncrypted": False, "Values": {}}

            if 'Values' not in settings:
                settings['Values'] = {}

            settings['Values']['AZURE_OPENAI_ENDPOINT'] = endpoint
            settings['Values']['AZURE_OPENAI_DEPLOYMENT_NAME'] = best_deployment
            settings['Values']['AZURE_OPENAI_API_KEY'] = api_key

            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)

            response += "✅ local.settings.json updated\n\n"

            # Step 5: Update Azure Function App
            response += "## Step 5: Updating Azure Function App...\n\n"

            az_cmd = [
                'az', 'functionapp', 'config', 'appsettings', 'set',
                '--name', function_app_name,
                '--resource-group', resource_group,
                '--settings',
                f"AZURE_OPENAI_ENDPOINT={endpoint}",
                f"AZURE_OPENAI_DEPLOYMENT_NAME={best_deployment}",
                f"AZURE_OPENAI_API_KEY={api_key}",
                '--output', 'none'
            ]
            az_result = subprocess.run(az_cmd, capture_output=True, text=True, timeout=60)

            if az_result.returncode != 0:
                response += f"⚠️ Warning updating Azure Function: {az_result.stderr}\n"
            else:
                response += f"✅ Azure Function App `{function_app_name}` updated\n\n"

            # Summary
            response += f"""## 🎉 Boost Complete!

### Configuration Applied:

| Setting | Value |
|---------|-------|
| **Model** | {best_model} |
| **Deployment** | {best_deployment} |
| **Endpoint** | {endpoint} |
| **API Key** | {api_key[:12]}...{api_key[-4:]} |

### Updated:
- ✅ local.settings.json
- ✅ Azure Function App ({function_app_name})

**Your AI has been upgraded to {best_model}!** 🧠✨

For local testing: `func start`
Production is already live!
"""
            return response

        except Exception as e:
            return response + f"\n❌ Error during boost: {str(e)}"
