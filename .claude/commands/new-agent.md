# Create New Agent for Copilot Agent 365

You are creating a new agent for the Copilot Agent 365 system.

## Agent Template

Create a new file in `agents/` folder:

```python
from agents.basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager  # If needed

class MyNewAgent(BasicAgent):
    def __init__(self):
        self.name = 'MyNewAgent'  # Must match the class conceptually
        self.metadata = {
            "name": self.name,
            "description": "Clear description of what this agent does - GPT uses this to decide when to call it",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of parameter 1"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Description of parameter 2"
                    }
                },
                "required": ["param1"]  # List required parameters
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        """
        Execute the agent's task.

        Args:
            **kwargs: Parameters defined in metadata

        Returns:
            str: Result to be added to conversation context
        """
        param1 = kwargs.get('param1', '')
        param2 = kwargs.get('param2', 0)

        # Your logic here
        result = f"Processed {param1} with value {param2}"

        return result
```

## Key Requirements

1. **Inherit from BasicAgent** - `from agents.basic_agent import BasicAgent`
2. **Define self.name** - Unique identifier for the agent
3. **Define self.metadata** - OpenAI function schema format
4. **Implement perform()** - Returns string result
5. **Call super().__init__()** - Pass name and metadata

## Metadata Schema

```python
metadata = {
    "name": "AgentName",           # Required: matches self.name
    "description": "What it does", # Required: GPT uses this
    "parameters": {
        "type": "object",          # Required: always "object"
        "properties": {            # Define each parameter
            "param": {
                "type": "string",  # string, integer, boolean, array, object
                "description": "What this param is for",
                "enum": ["a", "b"] # Optional: limit to specific values
            }
        },
        "required": ["param"]      # List of required param names
    }
}
```

## Using Storage

```python
from utils.storage_factory import get_storage_manager

class StorageAgent(BasicAgent):
    def __init__(self):
        self.storage = get_storage_manager()
        # ... rest of init

    def perform(self, **kwargs):
        # Read from storage
        data = self.storage.read_json()

        # Write to storage
        self.storage.write_json({"key": "value"})

        # File operations
        content = self.storage.read_file("directory", "file.txt")
        self.storage.write_file("directory", "file.txt", "content")
```

## Agent Request
$ARGUMENTS
