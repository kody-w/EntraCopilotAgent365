from agents.basic_agent import BasicAgent
import logging
import json
import os
import subprocess
import re
from typing import Any, Dict, Optional

class WorkflowRunnerAgent(BasicAgent):
    """
    Workflow Runner Agent - Executes workflow transcripts with runtime variable substitution.

    This agent reads structured workflow definitions (JSON) and executes them step-by-step,
    capturing outputs and feeding them into subsequent steps. This separates the "what to do"
    (workflow definition) from the "how to do it" (this executor).

    Key Features:
    - Variable substitution: ${step_id.output_name} or ${variable_name}
    - Multiple action types: az_command, update_json_file, template, evaluate, foreach
    - Error handling with on_error blocks
    - Conditional logic and validation
    - Sensitive data masking in logs
    - Dry-run mode for testing

    Workflow Format:
    {
        "name": "Workflow Name",
        "variables": { ... },
        "steps": [ ... ],
        "on_complete": { ... },
        "on_error": { ... }
    }
    """

    def __init__(self):
        self.name = 'WorkflowRunner'
        self.metadata = {
            "name": self.name,
            "description": """Workflow Runner Agent - Executes structured workflow transcripts.

ACTIONS:
- 'run': Execute a workflow from file or inline JSON
- 'list': List available workflows in the workflows/ directory
- 'validate': Validate a workflow without executing
- 'dry_run': Show what would happen without executing
- 'describe': Show detailed info about a workflow

This agent can run automation playbooks defined as JSON, with full variable substitution and error handling.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["run", "list", "validate", "dry_run", "describe"]
                    },
                    "workflow_name": {
                        "type": "string",
                        "description": "Name of workflow file (without .json) in workflows/ directory, e.g., 'iq_boost_workflow'"
                    },
                    "workflow_json": {
                        "type": "object",
                        "description": "Inline workflow definition (alternative to workflow_name)"
                    },
                    "variables": {
                        "type": "object",
                        "description": "Runtime variable overrides, e.g., {'function_app_name': 'my-app'}"
                    },
                    "start_from_step": {
                        "type": "string",
                        "description": "Step ID to start from (skip earlier steps)"
                    },
                    "stop_at_step": {
                        "type": "string",
                        "description": "Step ID to stop at (skip later steps)"
                    }
                },
                "required": ["action"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

        # Workflow directory
        self.workflows_dir = "workflows"

        # Runtime context for variable storage
        self.context: Dict[str, Any] = {}
        self.step_outputs: Dict[str, Dict[str, Any]] = {}

    def perform(self, **kwargs):
        action = kwargs.get('action', 'list')

        try:
            if action == 'list':
                return self._list_workflows()
            elif action == 'describe':
                return self._describe_workflow(kwargs)
            elif action == 'validate':
                return self._validate_workflow(kwargs)
            elif action == 'dry_run':
                return self._dry_run_workflow(kwargs)
            elif action == 'run':
                return self._run_workflow(kwargs)
            else:
                return f"Unknown action: {action}"
        except Exception as e:
            logging.error(f"WorkflowRunner error: {str(e)}")
            return f"Error: {str(e)}"

    def _list_workflows(self) -> str:
        """List available workflows in the workflows directory"""
        try:
            if not os.path.exists(self.workflows_dir):
                os.makedirs(self.workflows_dir)
                return f"No workflows found. Created {self.workflows_dir}/ directory."

            workflows = [f for f in os.listdir(self.workflows_dir) if f.endswith('.json')]

            if not workflows:
                return f"No workflows found in {self.workflows_dir}/"

            response = f"# 📋 Available Workflows\n\n"

            for wf_file in workflows:
                wf_path = os.path.join(self.workflows_dir, wf_file)
                try:
                    with open(wf_path, 'r') as f:
                        wf = json.load(f)
                    name = wf.get('name', wf_file)
                    desc = wf.get('description', 'No description')[:80]
                    steps = len(wf.get('steps', []))
                    response += f"### {wf_file.replace('.json', '')}\n"
                    response += f"- **Name:** {name}\n"
                    response += f"- **Description:** {desc}\n"
                    response += f"- **Steps:** {steps}\n\n"
                except:
                    response += f"### {wf_file} (error reading)\n\n"

            response += "\n**Run a workflow:**\n"
            response += "```\naction: \"run\"\nworkflow_name: \"iq_boost_workflow\"\n```"

            return response

        except Exception as e:
            return f"Error listing workflows: {str(e)}"

    def _load_workflow(self, params: Dict) -> Optional[Dict]:
        """Load workflow from file or inline JSON"""
        # Check for inline workflow
        if 'workflow_json' in params and params['workflow_json']:
            return params['workflow_json']

        # Load from file
        workflow_name = params.get('workflow_name')
        if not workflow_name:
            return None

        # Add .json if not present
        if not workflow_name.endswith('.json'):
            workflow_name += '.json'

        wf_path = os.path.join(self.workflows_dir, workflow_name)

        if not os.path.exists(wf_path):
            raise FileNotFoundError(f"Workflow not found: {wf_path}")

        with open(wf_path, 'r') as f:
            return json.load(f)

    def _describe_workflow(self, params: Dict) -> str:
        """Show detailed information about a workflow"""
        try:
            workflow = self._load_workflow(params)
            if not workflow:
                return "Error: workflow_name or workflow_json required"

            response = f"# 📖 Workflow: {workflow.get('name', 'Unnamed')}\n\n"
            response += f"**Description:** {workflow.get('description', 'No description')}\n"
            response += f"**Version:** {workflow.get('version', 'N/A')}\n"
            response += f"**Author:** {workflow.get('author', 'Unknown')}\n\n"

            # Variables
            variables = workflow.get('variables', {})
            if variables:
                response += "## Variables\n\n"
                response += "| Name | Type | Default | Description |\n"
                response += "|------|------|---------|-------------|\n"
                for var_name, var_def in variables.items():
                    if isinstance(var_def, dict):
                        vtype = var_def.get('type', 'any')
                        vdefault = str(var_def.get('default', ''))[:30]
                        vdesc = var_def.get('description', '')[:40]
                    else:
                        vtype = type(var_def).__name__
                        vdefault = str(var_def)[:30]
                        vdesc = ''
                    response += f"| {var_name} | {vtype} | {vdefault} | {vdesc} |\n"
                response += "\n"

            # Steps
            steps = workflow.get('steps', [])
            response += f"## Steps ({len(steps)})\n\n"
            for i, step in enumerate(steps, 1):
                step_id = step.get('id', f'step_{i}')
                step_name = step.get('name', step_id)
                step_action = step.get('action', 'unknown')
                step_desc = step.get('description', '')[:60]

                response += f"### {i}. {step_name}\n"
                response += f"- **ID:** `{step_id}`\n"
                response += f"- **Action:** `{step_action}`\n"
                response += f"- **Description:** {step_desc}\n"

                # Show outputs
                outputs = step.get('outputs', {})
                if outputs:
                    response += f"- **Outputs:** {', '.join(outputs.keys())}\n"

                response += "\n"

            return response

        except Exception as e:
            return f"Error describing workflow: {str(e)}"

    def _validate_workflow(self, params: Dict) -> str:
        """Validate a workflow without executing"""
        try:
            workflow = self._load_workflow(params)
            if not workflow:
                return "Error: workflow_name or workflow_json required"

            errors = []
            warnings = []

            # Check required fields
            if 'name' not in workflow:
                warnings.append("Missing 'name' field")
            if 'steps' not in workflow or not workflow['steps']:
                errors.append("Missing or empty 'steps' array")

            # Check steps
            step_ids = set()
            for i, step in enumerate(workflow.get('steps', [])):
                step_id = step.get('id', f'step_{i}')

                # Check for duplicate IDs
                if step_id in step_ids:
                    errors.append(f"Duplicate step ID: {step_id}")
                step_ids.add(step_id)

                # Check required step fields
                if 'action' not in step:
                    errors.append(f"Step '{step_id}' missing 'action' field")

                # Validate variable references
                step_str = json.dumps(step)
                refs = re.findall(r'\$\{([^}]+)\}', step_str)
                for ref in refs:
                    parts = ref.split('.')
                    if len(parts) > 1:
                        ref_step = parts[0]
                        if ref_step not in step_ids and ref_step not in workflow.get('variables', {}):
                            # It's a forward reference or variable
                            pass  # Forward refs are OK

            # Generate report
            response = f"# ✅ Workflow Validation: {workflow.get('name', 'Unnamed')}\n\n"

            if errors:
                response += "## ❌ Errors\n"
                for err in errors:
                    response += f"- {err}\n"
                response += "\n"

            if warnings:
                response += "## ⚠️ Warnings\n"
                for warn in warnings:
                    response += f"- {warn}\n"
                response += "\n"

            if not errors and not warnings:
                response += "✅ Workflow is valid!\n\n"
            elif not errors:
                response += "✅ Workflow is valid (with warnings)\n\n"
            else:
                response += "❌ Workflow has errors\n\n"

            response += f"**Steps:** {len(workflow.get('steps', []))}\n"
            response += f"**Variables:** {len(workflow.get('variables', {}))}\n"

            return response

        except Exception as e:
            return f"Error validating workflow: {str(e)}"

    def _dry_run_workflow(self, params: Dict) -> str:
        """Show what would happen without executing"""
        try:
            workflow = self._load_workflow(params)
            if not workflow:
                return "Error: workflow_name or workflow_json required"

            runtime_vars = params.get('variables', {})

            response = f"# 🔍 Dry Run: {workflow.get('name', 'Unnamed')}\n\n"
            response += "**This shows what would happen without making changes.**\n\n"

            # Initialize context with workflow variables
            self.context = {}
            for var_name, var_def in workflow.get('variables', {}).items():
                if var_name in runtime_vars:
                    self.context[var_name] = runtime_vars[var_name]
                elif isinstance(var_def, dict):
                    self.context[var_name] = var_def.get('default')
                else:
                    self.context[var_name] = var_def

            response += "## Variables\n"
            for k, v in self.context.items():
                display_v = str(v)[:50] + '...' if len(str(v)) > 50 else str(v)
                response += f"- `{k}`: {display_v}\n"
            response += "\n"

            response += "## Execution Plan\n\n"

            for i, step in enumerate(workflow.get('steps', []), 1):
                step_id = step.get('id', f'step_{i}')
                step_name = step.get('name', step_id)
                step_action = step.get('action', 'unknown')

                response += f"### Step {i}: {step_name}\n"
                response += f"- **Action:** `{step_action}`\n"

                if step_action == 'az_command':
                    cmd = step.get('command', '')
                    resolved_cmd = self._resolve_variables(cmd)
                    response += f"- **Command:** `{resolved_cmd}`\n"

                elif step_action == 'update_json_file':
                    file_path = self._resolve_variables(step.get('file_path', ''))
                    response += f"- **File:** `{file_path}`\n"
                    response += f"- **Updates:** {list(step.get('updates', {}).keys())}\n"

                elif step_action == 'template':
                    response += f"- **Template:** (generates report)\n"

                outputs = step.get('outputs', {})
                if outputs:
                    response += f"- **Outputs:** {', '.join(outputs.keys())}\n"
                    # Simulate outputs for next steps
                    self.step_outputs[step_id] = {k: f"<{step_id}.{k}>" for k in outputs.keys()}

                response += "\n"

            response += "---\n"
            response += "**To execute:** Remove `dry_run` or use `action: \"run\"`\n"

            return response

        except Exception as e:
            return f"Error in dry run: {str(e)}"

    def _run_workflow(self, params: Dict) -> str:
        """Execute a workflow"""
        try:
            workflow = self._load_workflow(params)
            if not workflow:
                return "Error: workflow_name or workflow_json required"

            runtime_vars = params.get('variables', {})
            start_from = params.get('start_from_step')
            stop_at = params.get('stop_at_step')

            # Reset context
            self.context = {}
            self.step_outputs = {}

            # Initialize variables
            for var_name, var_def in workflow.get('variables', {}).items():
                if var_name in runtime_vars:
                    self.context[var_name] = runtime_vars[var_name]
                elif isinstance(var_def, dict):
                    self.context[var_name] = var_def.get('default')
                else:
                    self.context[var_name] = var_def

            response = f"# 🚀 Running: {workflow.get('name', 'Unnamed')}\n\n"

            steps = workflow.get('steps', [])
            started = start_from is None

            for i, step in enumerate(steps, 1):
                step_id = step.get('id', f'step_{i}')
                step_name = step.get('name', step_id)

                # Handle start_from
                if not started:
                    if step_id == start_from:
                        started = True
                    else:
                        response += f"⏭️ Skipping: {step_name}\n"
                        continue

                # Handle stop_at
                if stop_at and step_id == stop_at:
                    response += f"\n⏹️ Stopping at: {step_name}\n"
                    break

                response += f"\n## Step {i}: {step_name}\n"

                try:
                    result = self._execute_step(step)

                    # Store outputs
                    outputs = step.get('outputs', {})
                    self.step_outputs[step_id] = result.get('outputs', {})

                    # Check for sensitive data
                    is_sensitive = step.get('sensitive', False)

                    if result.get('success'):
                        response += f"✅ Success\n"

                        # Show outputs (mask sensitive)
                        for out_name, out_value in self.step_outputs[step_id].items():
                            if is_sensitive:
                                display_val = "********"
                            else:
                                display_val = str(out_value)[:100]
                                if len(str(out_value)) > 100:
                                    display_val += "..."
                            response += f"   - `{out_name}`: {display_val}\n"
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        response += f"❌ Error: {error_msg}\n"

                        # Check on_error handler
                        on_error = step.get('on_error', {})
                        if on_error.get('abort', True):
                            response += f"\n**Workflow aborted:** {on_error.get('message', error_msg)}\n"
                            return response
                        else:
                            response += f"   (continuing despite error)\n"

                    # Validation
                    validation = step.get('validation', {})
                    if validation:
                        condition = validation.get('condition', '')
                        resolved_condition = self._resolve_variables(condition)
                        # Simple evaluation (for demo - in production use safe eval)
                        try:
                            if not self._eval_condition(resolved_condition):
                                error_msg = validation.get('error_message', 'Validation failed')
                                response += f"⚠️ Validation failed: {error_msg}\n"
                                if validation.get('abort', True):
                                    return response
                        except:
                            pass

                except Exception as e:
                    response += f"❌ Exception: {str(e)}\n"
                    on_error = step.get('on_error', {})
                    if on_error.get('abort', True):
                        return response

            # On complete
            on_complete = workflow.get('on_complete', {})
            if on_complete.get('action') == 'return':
                value_template = on_complete.get('value', '')
                final_value = self._resolve_variables(value_template)
                response += f"\n---\n\n{final_value}"

            return response

        except Exception as e:
            logging.error(f"Workflow execution error: {str(e)}")
            return f"Error running workflow: {str(e)}"

    def _execute_step(self, step: Dict) -> Dict:
        """Execute a single workflow step"""
        action = step.get('action', '')

        if action == 'az_command':
            return self._exec_az_command(step)
        elif action == 'update_json_file':
            return self._exec_update_json_file(step)
        elif action == 'template':
            return self._exec_template(step)
        elif action == 'evaluate':
            return self._exec_evaluate(step)
        elif action == 'foreach':
            return self._exec_foreach(step)
        else:
            return {'success': False, 'error': f"Unknown action: {action}"}

    def _exec_az_command(self, step: Dict) -> Dict:
        """Execute an Azure CLI command"""
        try:
            command = step.get('command', '')
            resolved_cmd = self._resolve_variables(command)

            # Split command for subprocess
            # Use shell=True for complex commands with pipes
            result = subprocess.run(
                resolved_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr or f"Command failed with code {result.returncode}",
                    'outputs': {}
                }

            # Parse outputs
            outputs = {}
            output_defs = step.get('outputs', {})

            try:
                # Try to parse as JSON
                data = json.loads(result.stdout) if result.stdout.strip() else {}
            except json.JSONDecodeError:
                # Plain text output
                data = result.stdout.strip()

            for out_name, out_path in output_defs.items():
                if out_path == '$':
                    outputs[out_name] = data
                elif out_path == '$.length':
                    outputs[out_name] = len(data) if isinstance(data, list) else 0
                elif out_path.startswith('$.'):
                    # Simple JSON path (just first level)
                    key = out_path[2:]
                    outputs[out_name] = data.get(key) if isinstance(data, dict) else data
                else:
                    outputs[out_name] = data

            return {'success': True, 'outputs': outputs}

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out', 'outputs': {}}
        except Exception as e:
            return {'success': False, 'error': str(e), 'outputs': {}}

    def _exec_update_json_file(self, step: Dict) -> Dict:
        """Update a JSON file with new values"""
        try:
            file_path = self._resolve_variables(step.get('file_path', ''))
            updates = step.get('updates', {})

            # Read existing file
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            # Store previous values for output
            previous = {}

            # Apply updates
            for key_path, value in updates.items():
                resolved_value = self._resolve_variables(str(value))

                # Handle nested keys like "Values.AZURE_OPENAI_ENDPOINT"
                keys = key_path.split('.')
                current = data

                # Store previous value
                try:
                    prev_current = data
                    for k in keys[:-1]:
                        prev_current = prev_current.get(k, {})
                    previous[key_path] = prev_current.get(keys[-1])
                except:
                    previous[key_path] = None

                # Set new value
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = resolved_value

            # Write back
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            outputs = {'updated': True}
            outputs.update({f"previous_{k.replace('.', '_')}": v for k, v in previous.items()})

            return {'success': True, 'outputs': outputs}

        except Exception as e:
            return {'success': False, 'error': str(e), 'outputs': {}}

    def _exec_template(self, step: Dict) -> Dict:
        """Render a template with variable substitution"""
        try:
            template = step.get('template', '')
            resolved = self._resolve_variables(template)

            outputs = {}
            for out_name in step.get('outputs', {}).keys():
                outputs[out_name] = resolved

            return {'success': True, 'outputs': outputs}

        except Exception as e:
            return {'success': False, 'error': str(e), 'outputs': {}}

    def _exec_evaluate(self, step: Dict) -> Dict:
        """Evaluate logic to find best match"""
        try:
            logic = step.get('logic', {})
            logic_type = logic.get('type', '')

            if logic_type == 'priority_match':
                source_ref = logic.get('source', '')
                source = self._resolve_variable_ref(source_ref)
                priorities = logic.get('priorities', [])
                match_field = logic.get('match_field', '')

                if not isinstance(source, list):
                    source = [source] if source else []

                # Find best match
                for priority in priorities:
                    for item in source:
                        field_value = self._get_nested(item, match_field)
                        if priority.lower() in str(field_value).lower():
                            outputs = {}
                            for out_name, out_path in step.get('outputs', {}).items():
                                outputs[out_name] = self._get_nested(item, out_path.replace('$.', ''))
                            return {'success': True, 'outputs': outputs}

                return {'success': False, 'error': 'No matching item found', 'outputs': {}}

            return {'success': False, 'error': f'Unknown logic type: {logic_type}', 'outputs': {}}

        except Exception as e:
            return {'success': False, 'error': str(e), 'outputs': {}}

    def _exec_foreach(self, step: Dict) -> Dict:
        """Execute steps for each item in a collection"""
        try:
            collection_ref = step.get('collection', '')
            collection = self._resolve_variable_ref(collection_ref)

            if not isinstance(collection, list):
                collection = [collection] if collection else []

            all_results = []

            for item in collection:
                # Set the loop variable
                var_name = step.get('as', 'item')
                self.context[var_name] = item

                # Execute sub-steps
                for sub_step in step.get('steps', []):
                    result = self._execute_step(sub_step)
                    if result.get('success'):
                        all_results.append(result.get('outputs', {}))

            outputs = {}
            for out_name, out_expr in step.get('outputs', {}).items():
                if 'flatten' in out_expr:
                    outputs[out_name] = all_results
                else:
                    outputs[out_name] = all_results

            return {'success': True, 'outputs': outputs}

        except Exception as e:
            return {'success': False, 'error': str(e), 'outputs': {}}

    def _resolve_variables(self, text: str) -> str:
        """Resolve ${variable} references in text"""
        if not text or not isinstance(text, str):
            return str(text) if text else ''

        def replace_var(match):
            var_ref = match.group(1)
            value = self._resolve_variable_ref(var_ref)
            return str(value) if value is not None else match.group(0)

        return re.sub(r'\$\{([^}]+)\}', replace_var, text)

    def _resolve_variable_ref(self, ref: str) -> Any:
        """Resolve a variable reference like 'step_id.output_name' or 'variable_name'"""
        parts = ref.split('.')

        # Check step outputs first
        if parts[0] in self.step_outputs:
            current = self.step_outputs[parts[0]]
            for part in parts[1:]:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return current

        # Check context variables
        if parts[0] in self.context:
            current = self.context[parts[0]]
            for part in parts[1:]:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return current

        return None

    def _get_nested(self, obj: Any, path: str) -> Any:
        """Get a nested value from an object using dot notation"""
        if not path:
            return obj

        parts = path.split('.')
        current = obj

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                return None

        return current

    def _eval_condition(self, condition: str) -> bool:
        """Safely evaluate a simple condition"""
        # Very basic evaluation for demo
        # In production, use a proper expression parser
        try:
            # Handle simple comparisons
            if '>' in condition:
                parts = condition.split('>')
                return float(parts[0].strip()) > float(parts[1].strip())
            elif '<' in condition:
                parts = condition.split('<')
                return float(parts[0].strip()) < float(parts[1].strip())
            elif '==' in condition:
                parts = condition.split('==')
                return parts[0].strip() == parts[1].strip()
            elif condition.lower() in ('true', '1'):
                return True
            elif condition.lower() in ('false', '0'):
                return False
            return bool(condition)
        except:
            return False
