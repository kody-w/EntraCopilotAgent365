"""
Context Analyzer Agent - Displays current payload/context usage visualization
Similar to Claude Code's /context command output

This agent is self-sufficient - it reads all necessary data directly from:
- Environment variables (model config)
- File system (agents directory)
- Storage (memory files)
- API request (conversation history via kwargs)
"""
import logging
import json
import os
import sys
from agents.basic_agent import BasicAgent


class ContextAnalyzerAgent(BasicAgent):
    def __init__(self):
        self.name = 'ContextAnalyzer'
        self.metadata = {
            "name": self.name,
            "description": "Analyzes and displays current context/payload usage with a visual breakdown of token allocation. Shows system prompt, tools, memory, messages, and free space. Simply call this agent to see context usage - no parameters needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_guid": {
                        "type": "string",
                        "description": "User GUID for memory lookup (optional, auto-detected from request)"
                    }
                },
                "required": []
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

        # Model token limits lookup
        self.model_token_limits = {
            'gpt-5-chat': 200000,
            'gpt-5': 200000,
            'gpt-4o': 128000,
            'gpt-4-turbo': 128000,
            'gpt-4': 8192,
            'gpt-4-32k': 32768,
            'gpt-35-turbo': 16385,
            'gpt-35-turbo-16k': 16385,
        }

    def perform(self, **kwargs):
        """
        Analyzes context usage by gathering data from multiple sources automatically.
        """
        # Extract conversation history from kwargs (passed via API request)
        conversation_history = kwargs.get('conversation_history', [])
        user_guid = kwargs.get('user_guid')

        # Gather all data deterministically
        model_info = self._get_model_info()
        agent_info = self._get_agent_info()
        memory_info = self._get_memory_info(user_guid)
        system_prompt_info = self._get_system_prompt_info()
        message_info = self._analyze_messages(conversation_history)

        # Calculate token estimates
        token_counts = {
            'system_prompt': system_prompt_info['estimated_tokens'],
            'agent_tools': agent_info['estimated_tokens'],
            'memory': memory_info['estimated_tokens'],
            'messages': message_info['estimated_tokens'],
            'user_messages': message_info['user_count'],
            'assistant_messages': message_info['assistant_count'],
            'total_messages': message_info['total_count']
        }

        # Generate visual output
        return self._generate_context_display(
            token_counts,
            model_info['max_tokens'],
            model_info['model_name'],
            agent_info,
            memory_info
        )

    def _get_model_info(self):
        """Get model configuration from environment variables"""
        deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-5-chat')

        # Determine max tokens based on model
        max_tokens = self.model_token_limits.get(deployment_name, 200000)

        # Check for common model name patterns
        for model_key, limit in self.model_token_limits.items():
            if model_key in deployment_name.lower():
                max_tokens = limit
                break

        return {
            'model_name': deployment_name,
            'max_tokens': max_tokens,
            'api_version': os.environ.get('AZURE_OPENAI_API_VERSION', 'unknown')
        }

    def _get_agent_info(self):
        """Scan agents directory and storage to enumerate available agents"""
        agents = []
        estimated_tokens = 0

        # Scan local agents directory
        try:
            agents_dir = os.path.join(os.path.dirname(__file__), '.')
            if os.path.exists(agents_dir):
                for file in os.listdir(agents_dir):
                    if file.endswith('_agent.py') and file != 'basic_agent.py':
                        agent_name = file.replace('_agent.py', '').replace('_', ' ').title()
                        agents.append({
                            'name': agent_name,
                            'file': file,
                            'source': 'local'
                        })
                        # Estimate ~500 tokens per agent for function metadata
                        estimated_tokens += 500
        except Exception as e:
            logging.warning(f"Could not scan local agents: {e}")

        # Try to scan Azure storage agents
        try:
            from utils.storage_factory import get_storage_manager
            storage = get_storage_manager()
            storage_agents = storage.list_files('agents')
            for file in storage_agents:
                if file.name.endswith('_agent.py'):
                    agent_name = file.name.replace('_agent.py', '').replace('_', ' ').title()
                    # Avoid duplicates
                    if not any(a['file'] == file.name for a in agents):
                        agents.append({
                            'name': agent_name,
                            'file': file.name,
                            'source': 'storage'
                        })
                        estimated_tokens += 500
        except Exception as e:
            logging.debug(f"Could not scan storage agents: {e}")

        return {
            'agents': agents,
            'count': len(agents),
            'estimated_tokens': estimated_tokens
        }

    def _get_memory_info(self, user_guid=None):
        """Read memory content size from storage"""
        memory_content = ""
        estimated_tokens = 0

        try:
            from utils.storage_factory import get_storage_manager
            storage = get_storage_manager()

            # Set context for user-specific memory
            if user_guid:
                storage.set_memory_context(user_guid)

            # Read memory JSON
            memory_data = storage.read_json()
            if memory_data:
                memory_content = json.dumps(memory_data)
                estimated_tokens = max(1, len(memory_content) // 4)
        except Exception as e:
            logging.debug(f"Could not read memory: {e}")

        return {
            'content_length': len(memory_content),
            'estimated_tokens': estimated_tokens,
            'has_memory': estimated_tokens > 0
        }

    def _get_system_prompt_info(self):
        """Reconstruct system prompt size from environment config"""
        assistant_name = os.environ.get('ASSISTANT_NAME', 'BusinessInsightBot')
        characteristic = os.environ.get('CHARACTERISTIC_DESCRIPTION', 'helpful business assistant')

        # Estimate the system prompt structure (base template + config)
        # The actual system prompt includes instructions, agent descriptions, memory context, etc.
        base_prompt_estimate = 500  # Base instructions
        name_tokens = len(assistant_name) // 4
        char_tokens = len(characteristic) // 4

        # Add estimate for agent instructions and formatting
        total_estimate = base_prompt_estimate + name_tokens + char_tokens

        return {
            'assistant_name': assistant_name,
            'characteristic': characteristic,
            'estimated_tokens': total_estimate
        }

    def _analyze_messages(self, conversation_history):
        """Analyze conversation history for token usage"""
        total_tokens = 0
        user_count = 0
        assistant_count = 0

        for msg in conversation_history:
            if isinstance(msg, dict):
                content = msg.get('content', '')
                role = msg.get('role', '')

                # Estimate tokens (~4 chars per token)
                if isinstance(content, str):
                    total_tokens += max(1, len(content) // 4)
                elif isinstance(content, (dict, list)):
                    total_tokens += max(1, len(json.dumps(content)) // 4)

                # Add overhead for message structure
                total_tokens += 4  # role, separators

                if role == 'user':
                    user_count += 1
                elif role == 'assistant':
                    assistant_count += 1

        return {
            'estimated_tokens': total_tokens,
            'user_count': user_count,
            'assistant_count': assistant_count,
            'total_count': len(conversation_history)
        }

    def _generate_context_display(self, token_counts, max_tokens, model_name, agent_info, memory_info):
        """Generate a visual context usage display similar to Claude Code's /context"""

        # Calculate totals
        used_tokens = (
            token_counts['system_prompt'] +
            token_counts['agent_tools'] +
            token_counts['memory'] +
            token_counts['messages']
        )

        free_tokens = max(0, max_tokens - used_tokens)
        buffer_tokens = int(max_tokens * 0.15)
        effective_free = max(0, free_tokens - buffer_tokens)
        usage_percent = (used_tokens / max_tokens) * 100 if max_tokens > 0 else 0

        # Format helpers
        def fmt_tokens(n):
            if n >= 1000:
                return f"{n/1000:.1f}k"
            return str(int(n))

        def fmt_pct(n):
            pct = (n / max_tokens) * 100 if max_tokens > 0 else 0
            return f"{pct:.1f}%"

        # Create visual block bar (like Claude Code) - 10 blocks per row, 4 rows
        def make_visual_grid(percentages):
            """Create a 4-row visual grid showing token allocation"""
            total_blocks = 40
            rows = []

            # Calculate blocks for each category
            blocks = []
            for pct in percentages:
                num_blocks = int((pct / 100) * total_blocks)
                blocks.append(num_blocks)

            # Ensure we don't exceed total
            while sum(blocks) > total_blocks:
                max_idx = blocks.index(max(blocks))
                blocks[max_idx] -= 1

            # Build the grid string
            all_blocks = []
            colors = ['🟦', '🟧', '🟩', '🟨', '⬜', '⬛']  # sys, tools, mem, msg, free, buffer

            for i, count in enumerate(blocks):
                all_blocks.extend([colors[i]] * count)

            # Pad with buffer/free
            remaining = total_blocks - len(all_blocks)
            buffer_blocks = min(remaining, int(total_blocks * 0.15))
            free_blocks = remaining - buffer_blocks
            all_blocks.extend(['⬜'] * free_blocks)
            all_blocks.extend(['⬛'] * buffer_blocks)

            # Format into 4 rows of 10
            for i in range(4):
                start = i * 10
                rows.append(''.join(all_blocks[start:start + 10]))

            return rows

        # Calculate percentages
        sys_pct = (token_counts['system_prompt'] / max_tokens) * 100 if max_tokens > 0 else 0
        tools_pct = (token_counts['agent_tools'] / max_tokens) * 100 if max_tokens > 0 else 0
        mem_pct = (token_counts['memory'] / max_tokens) * 100 if max_tokens > 0 else 0
        msg_pct = (token_counts['messages'] / max_tokens) * 100 if max_tokens > 0 else 0
        free_pct = (effective_free / max_tokens) * 100 if max_tokens > 0 else 0
        buffer_pct = (buffer_tokens / max_tokens) * 100 if max_tokens > 0 else 0

        grid_rows = make_visual_grid([sys_pct, tools_pct, mem_pct, msg_pct, free_pct, buffer_pct])

        # Build output
        lines = []
        lines.append("")
        lines.append("  Context Usage")
        lines.append("  ─────────────────────────────────────────────────────────")
        lines.append(f"        {grid_rows[0]}    {model_name} · {fmt_tokens(used_tokens)}/{fmt_tokens(max_tokens)} tokens ({usage_percent:.0f}%)")
        lines.append(f"        {grid_rows[1]}")
        lines.append(f"        {grid_rows[2]}")
        lines.append(f"        {grid_rows[3]}")
        lines.append("")

        # Breakdown table
        lines.append(f"        🟦 System prompt:    {fmt_tokens(token_counts['system_prompt']):>7} tokens ({fmt_pct(token_counts['system_prompt']):>5})")
        lines.append(f"        🟧 Agent tools:      {fmt_tokens(token_counts['agent_tools']):>7} tokens ({fmt_pct(token_counts['agent_tools']):>5})")
        lines.append(f"        🟩 Memory files:     {fmt_tokens(token_counts['memory']):>7} tokens ({fmt_pct(token_counts['memory']):>5})")
        lines.append(f"        🟨 Messages:         {fmt_tokens(token_counts['messages']):>7} tokens ({fmt_pct(token_counts['messages']):>5})")
        lines.append(f"        ⬜ Free space:       {fmt_tokens(effective_free):>7} ({fmt_pct(effective_free):>5})")
        lines.append(f"        ⬛ Buffer reserve:   {fmt_tokens(buffer_tokens):>7} ({fmt_pct(buffer_tokens):>5})")
        lines.append("")

        # Agent tools section
        lines.append("  Agent Tools · /agents")
        lines.append("  ─────────────────────────────────────────────────────────")

        if agent_info['agents']:
            local_agents = [a for a in agent_info['agents'] if a['source'] == 'local']
            storage_agents = [a for a in agent_info['agents'] if a['source'] == 'storage']

            for agent in local_agents[:6]:
                lines.append(f"  ├─ {agent['name']}: ~500 tokens")
            if len(local_agents) > 6:
                lines.append(f"  ├─ ... and {len(local_agents) - 6} more local agents")

            if storage_agents:
                lines.append(f"  │")
                for agent in storage_agents[:3]:
                    lines.append(f"  ├─ {agent['name']} (cloud): ~500 tokens")
                if len(storage_agents) > 3:
                    lines.append(f"  ├─ ... and {len(storage_agents) - 3} more cloud agents")

            lines.append(f"  └─ Total: {fmt_tokens(token_counts['agent_tools'])} tokens")
        else:
            lines.append("  └─ No agents loaded")
        lines.append("")

        # Memory section
        lines.append("  Memory · /memory")
        lines.append("  ─────────────────────────────────────────────────────────")
        if memory_info['has_memory']:
            lines.append(f"  └─ User memory: {fmt_tokens(token_counts['memory'])} tokens")
        else:
            lines.append("  └─ No memory loaded")
        lines.append("")

        # Messages section
        lines.append("  Messages")
        lines.append("  ─────────────────────────────────────────────────────────")
        lines.append(f"  ├─ 👤 User messages:      {token_counts['user_messages']}")
        lines.append(f"  ├─ 🤖 Assistant messages: {token_counts['assistant_messages']}")
        lines.append(f"  └─ Total: {token_counts['total_messages']} messages · {fmt_tokens(token_counts['messages'])} tokens")
        lines.append("")

        # Warning if needed
        if usage_percent > 75:
            lines.append("  ─────────────────────────────────────────────────────────")
            if usage_percent > 90:
                lines.append("  ⚠️  Critical: Context nearly full! Consider clearing history.")
            else:
                lines.append("  ⚠️  Warning: Context usage is high.")
            lines.append("")

        return "\n".join(lines)


# For testing
if __name__ == "__main__":
    # Set test environment variables
    os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = 'gpt-5-chat'
    os.environ['ASSISTANT_NAME'] = 'Copilot Agent 365'
    os.environ['CHARACTERISTIC_DESCRIPTION'] = 'An enterprise AI assistant'

    agent = ContextAnalyzerAgent()

    # Test with sample conversation
    test_history = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well! How can I help you today?"},
        {"role": "user", "content": "Show me the context usage"},
    ]

    result = agent.perform(conversation_history=test_history)
    print(result)
