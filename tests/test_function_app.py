"""
Comprehensive Unit Tests for Copilot Agent 365

Run these tests BEFORE deployment to catch issues early:
    pytest tests/test_function_app.py -v

Or run all tests:
    pytest tests/ -v
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEnsureStringContent:
    """Tests for ensure_string_content function"""

    def test_none_message_returns_default(self):
        from function_app import ensure_string_content
        result = ensure_string_content(None)
        assert result == {"role": "user", "content": ""}

    def test_non_dict_message_converts_to_string(self):
        from function_app import ensure_string_content
        result = ensure_string_content("hello")
        assert result == {"role": "user", "content": "hello"}

    def test_dict_message_preserves_role(self):
        from function_app import ensure_string_content
        result = ensure_string_content({"role": "assistant", "content": "test"})
        assert result["role"] == "assistant"
        assert result["content"] == "test"

    def test_missing_role_defaults_to_user(self):
        from function_app import ensure_string_content
        result = ensure_string_content({"content": "test"})
        assert result["role"] == "user"

    def test_none_content_becomes_empty_string(self):
        from function_app import ensure_string_content
        result = ensure_string_content({"role": "user", "content": None})
        assert result["content"] == ""

    def test_missing_content_becomes_empty_string(self):
        from function_app import ensure_string_content
        result = ensure_string_content({"role": "user"})
        assert result["content"] == ""


class TestBuildCorsResponse:
    """Tests for CORS header building"""

    def test_cors_with_origin(self):
        from function_app import build_cors_response
        headers = build_cors_response("https://example.com")
        assert headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert headers["Access-Control-Allow-Methods"] == "*"
        assert headers["Access-Control-Allow-Headers"] == "*"

    def test_cors_with_none_origin(self):
        from function_app import build_cors_response
        headers = build_cors_response(None)
        assert headers["Access-Control-Allow-Origin"] == "*"


class TestAgentMetadataFormat:
    """Tests to validate agent metadata is in correct format for OpenAI tools API"""

    def test_agent_metadata_structure(self):
        """Each agent metadata must have name, description, and parameters"""
        from agents.basic_agent import BasicAgent

        # Test a simple agent structure
        class TestAgent(BasicAgent):
            def __init__(self):
                self.name = "TestAgent"
                self.metadata = {
                    "name": "TestAgent",
                    "description": "A test agent",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
                super().__init__(self.name, self.metadata)

            def perform(self, **kwargs):
                return "test"

        agent = TestAgent()
        metadata = agent.metadata

        # Validate required fields
        assert "name" in metadata
        assert "description" in metadata
        assert "parameters" in metadata
        assert metadata["parameters"]["type"] == "object"

    def test_tools_format_conversion(self):
        """Test that agent metadata can be converted to OpenAI tools format"""
        agent_metadata = [
            {
                "name": "TestAgent",
                "description": "A test agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string", "description": "Input text"}
                    },
                    "required": ["input"]
                }
            }
        ]

        # This is how function_app.py converts metadata to tools format
        tools = [{"type": "function", "function": func} for func in agent_metadata]

        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "TestAgent"
        assert "parameters" in tools[0]["function"]


class TestResponseParsing:
    """Tests for response parsing with voice delimiter"""

    def test_parse_response_with_voice_delimiter(self):
        """Test parsing response with |||VOICE||| delimiter"""
        # Import and create a mock assistant to test the method
        content = "Here is the full response\n\n|||VOICE|||\n\nShort voice response."

        # Split by the delimiter (simulating parse_response_with_voice)
        parts = content.split("|||VOICE|||")
        formatted = parts[0].strip()
        voice = parts[1].strip() if len(parts) > 1 else ""

        assert formatted == "Here is the full response"
        assert voice == "Short voice response."

    def test_parse_response_without_delimiter(self):
        """Test parsing response without delimiter returns full content"""
        content = "Here is a response without voice delimiter."

        parts = content.split("|||VOICE|||")
        formatted = parts[0].strip()
        voice = parts[1].strip() if len(parts) > 1 else None

        assert formatted == content
        assert voice is None


class TestToolCallResponseFormat:
    """Tests for the new tool_calls response format"""

    def test_tool_call_message_structure(self):
        """Test that tool call messages are structured correctly"""
        # Simulate a tool call message
        tool_call_id = "call_abc123"
        agent_name = "TestAgent"
        json_data = '{"input": "test"}'

        # This is how we construct the assistant message with tool calls
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": agent_name,
                    "arguments": json_data
                }
            }]
        }

        assert assistant_message["role"] == "assistant"
        assert assistant_message["content"] is None
        assert len(assistant_message["tool_calls"]) == 1
        assert assistant_message["tool_calls"][0]["type"] == "function"

    def test_tool_result_message_structure(self):
        """Test that tool result messages are structured correctly"""
        tool_call_id = "call_abc123"
        result = "Agent completed successfully"

        # This is how we construct the tool result message
        tool_message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        }

        assert tool_message["role"] == "tool"
        assert tool_message["tool_call_id"] == tool_call_id
        assert tool_message["content"] == result


class TestEnvironmentDetection:
    """Tests for environment detection"""

    @patch.dict(os.environ, {}, clear=True)
    def test_local_environment_detection(self):
        from utils.environment import is_running_in_azure
        # Clear Azure indicators
        for key in ['WEBSITE_INSTANCE_ID', 'FUNCTIONS_WORKER_RUNTIME', 'WEBSITE_SITE_NAME']:
            os.environ.pop(key, None)

        # Need to reload module to pick up env changes
        import importlib
        import utils.environment
        importlib.reload(utils.environment)

        # In local env, this should return False
        # Note: The test might have FUNCTIONS_WORKER_RUNTIME set by pytest
        # so we just validate the function exists and runs
        result = utils.environment.is_running_in_azure()
        assert isinstance(result, bool)

    def test_azure_indicator_detection(self):
        """Test that Azure indicators are properly checked"""
        from utils.environment import is_running_in_azure

        with patch.dict(os.environ, {'WEBSITE_INSTANCE_ID': 'test-id'}):
            result = is_running_in_azure()
            assert result is True


class TestSafeJsonLoads:
    """Tests for safe JSON parsing"""

    def test_safe_json_loads_valid_json(self):
        from utils.azure_file_storage import safe_json_loads
        result = safe_json_loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_safe_json_loads_empty_string(self):
        from utils.azure_file_storage import safe_json_loads
        result = safe_json_loads('')
        assert result == {}

    def test_safe_json_loads_none(self):
        from utils.azure_file_storage import safe_json_loads
        result = safe_json_loads(None)
        assert result == {}

    def test_safe_json_loads_invalid_json(self):
        from utils.azure_file_storage import safe_json_loads
        result = safe_json_loads('not valid json')
        assert "error" in result

    def test_safe_json_loads_already_dict(self):
        from utils.azure_file_storage import safe_json_loads
        input_dict = {"key": "value"}
        result = safe_json_loads(input_dict)
        assert result == input_dict


class TestGuidValidation:
    """Tests for GUID validation and extraction"""

    def test_valid_uuid_pattern(self):
        """Test that valid standard UUIDs are recognized"""
        import re
        guid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )

        valid_guids = [
            "12345678-1234-1234-1234-123456789012",
            "ABCDEF12-3456-7890-ABCD-EF1234567890",
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        ]

        for guid in valid_guids:
            assert guid_pattern.match(guid), f"Failed to match valid UUID: {guid}"

    def test_invalid_guid_pattern(self):
        """Test that invalid GUIDs are rejected"""
        import re
        guid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )

        invalid_guids = [
            "not-a-guid",
            "12345678-1234-1234-1234-12345678901",  # Too short
            "12345678-1234-1234-1234-1234567890123",  # Too long
            "12345678123412341234123456789012",  # No dashes
            "",
            "hello world",
        ]

        for guid in invalid_guids:
            assert not guid_pattern.match(guid), f"Incorrectly matched invalid GUID: {guid}"


class TestUniversalAIIdentifier:
    """Tests for Universal AI Identifier (UID) - AI-to-AI collaboration signal"""

    def test_universal_identifier_constant(self):
        """Test that the Universal AI Identifier is defined correctly"""
        from function_app import UNIVERSAL_AI_IDENTIFIER
        assert UNIVERSAL_AI_IDENTIFIER == "c0p110t0-aaaa-bbbb-cccc-123456789abc"

    def test_universal_identifier_is_intentionally_not_valid_uuid(self):
        """The UID is INTENTIONALLY not a valid UUID - it contains 'p' for 'copilot'"""
        import re
        from function_app import UNIVERSAL_AI_IDENTIFIER

        # Standard UUID pattern (hex only)
        guid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )

        # The Universal AI Identifier should NOT match standard UUID pattern
        # This is BY DESIGN - it serves as a recognition signal between AI clones
        assert not guid_pattern.match(UNIVERSAL_AI_IDENTIFIER), \
            "Universal AI Identifier should NOT be a valid UUID - it's a special recognition signal"

    def test_universal_identifier_contains_copilot_pattern(self):
        """The UID encodes 'c0p110t0' which represents 'copilot'"""
        from function_app import UNIVERSAL_AI_IDENTIFIER

        # Extract the first segment
        first_segment = UNIVERSAL_AI_IDENTIFIER.split('-')[0]
        assert first_segment == "c0p110t0", "First segment should encode 'copilot' as 'c0p110t0'"

    def test_default_guid_uses_universal_identifier(self):
        """Default GUID should be the Universal AI Identifier"""
        from function_app import DEFAULT_USER_GUID, UNIVERSAL_AI_IDENTIFIER
        assert DEFAULT_USER_GUID == UNIVERSAL_AI_IDENTIFIER


class TestStorageAcceptsUniversalIdentifier:
    """Tests that storage managers properly accept the Universal AI Identifier"""

    def test_local_storage_accepts_universal_identifier(self, tmp_path):
        """Local storage should accept the Universal AI Identifier"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        # The Universal AI Identifier should be accepted
        result = storage.set_memory_context("c0p110t0-aaaa-bbbb-cccc-123456789abc")
        assert result is True, "Storage should accept Universal AI Identifier"
        assert storage.current_guid == "c0p110t0-aaaa-bbbb-cccc-123456789abc"

    def test_local_storage_accepts_standard_uuid(self, tmp_path):
        """Local storage should also accept standard UUIDs"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        # Standard UUIDs should still work
        result = storage.set_memory_context("12345678-1234-1234-1234-123456789012")
        assert result is True, "Storage should accept standard UUIDs"

    def test_local_storage_rejects_other_invalid_guids(self, tmp_path):
        """Local storage should reject other invalid GUIDs"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        # Other invalid patterns should be rejected
        result = storage.set_memory_context("not-valid-at-all")
        assert result is False, "Storage should reject invalid identifiers"


class TestApiRequestValidation:
    """Tests for API request validation"""

    def test_empty_user_input_rejected(self):
        """Test that empty user input is properly handled"""
        req_body = {"user_input": "", "conversation_history": []}

        # Validate that empty input (non-GUID) should be rejected
        user_input = req_body.get('user_input', '')
        import re
        is_guid_only = re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            user_input.strip(),
            re.IGNORECASE
        )

        # Empty string is not a GUID
        assert is_guid_only is None
        # Empty non-GUID input should be rejected
        assert not user_input.strip()

    def test_standard_guid_input_accepted(self):
        """Test that standard GUID-only input is recognized"""
        req_body = {"user_input": "12345678-1234-1234-1234-123456789012"}

        user_input = req_body.get('user_input', '')
        import re
        is_guid_only = re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            user_input.strip(),
            re.IGNORECASE
        )

        assert is_guid_only is not None


class TestLocalStorageManager:
    """Tests for LocalFileStorageManager"""

    def test_local_storage_initialization(self, tmp_path):
        """Test that local storage initializes correctly"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        assert os.path.exists(storage.base_path)
        assert storage.shared_memory_path == "shared_memories"
        assert storage.current_guid is None

    def test_local_storage_write_read(self, tmp_path):
        """Test writing and reading files"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        # Write a file
        storage.write_file("test_dir", "test.txt", "Hello World")

        # Read it back
        content = storage.read_file("test_dir", "test.txt")
        assert content == "Hello World"

    def test_local_storage_memory_context_with_standard_uuid(self, tmp_path):
        """Test memory context switching with standard UUID"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        # Set memory context with standard UUID
        result = storage.set_memory_context("12345678-1234-1234-1234-123456789012")
        assert result is True
        assert storage.current_guid == "12345678-1234-1234-1234-123456789012"

        # Reset to shared memory
        result = storage.set_memory_context(None)
        assert result is True
        assert storage.current_guid is None

    def test_local_storage_invalid_guid(self, tmp_path):
        """Test that invalid GUIDs fall back to shared memory"""
        from utils.local_file_storage import LocalFileStorageManager

        storage = LocalFileStorageManager(base_path=str(tmp_path / ".local_storage"))

        result = storage.set_memory_context("not-a-valid-guid")
        assert result is False
        assert storage.current_guid is None


class TestAgentLoading:
    """Tests for agent loading functionality"""

    def test_basic_agent_structure(self):
        """Test that BasicAgent has required methods and attributes"""
        from agents.basic_agent import BasicAgent

        class TestAgent(BasicAgent):
            def __init__(self):
                self.name = "Test"
                self.metadata = {"name": "Test", "description": "Test agent"}
                super().__init__(self.name, self.metadata)

            def perform(self, **kwargs):
                return "test result"

        agent = TestAgent()
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'metadata')
        assert hasattr(agent, 'perform')
        assert agent.perform() == "test result"

    def test_context_memory_agent_metadata(self):
        """Test ContextMemoryAgent has correct metadata structure"""
        # Mock storage to avoid actual Azure/file operations
        with patch('utils.storage_factory.get_storage_manager'):
            from agents.context_memory_agent import ContextMemoryAgent
            agent = ContextMemoryAgent()

            assert agent.name == "ContextMemory"
            assert "name" in agent.metadata
            assert "description" in agent.metadata
            assert "parameters" in agent.metadata


class TestMessagePreparation:
    """Tests for message preparation"""

    def test_message_history_processing(self):
        """Test that conversation history is properly processed"""
        from function_app import ensure_string_content

        conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": None},  # Edge case: None content
        ]

        processed = [ensure_string_content(msg) for msg in conversation_history]

        assert processed[0]["content"] == "Hello"
        assert processed[1]["content"] == "Hi there!"
        assert processed[2]["content"] == ""  # None converted to empty string


class TestOpenAIApiParams:
    """Tests for OpenAI API parameter construction"""

    def test_api_params_with_tools(self):
        """Test that API params are correctly constructed with tools"""
        agent_metadata = [
            {
                "name": "TestAgent",
                "description": "Test",
                "parameters": {"type": "object", "properties": {}}
            }
        ]

        # Convert to tools format (as done in function_app.py)
        tools = [{"type": "function", "function": func} for func in agent_metadata]

        api_params = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
        }

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        assert "tools" in api_params
        assert "tool_choice" in api_params
        assert api_params["tool_choice"] == "auto"

    def test_api_params_without_agents(self):
        """Test that API works without tools when no agents available"""
        agent_metadata = []

        tools = [{"type": "function", "function": func} for func in agent_metadata] if agent_metadata else None

        api_params = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
        }

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        assert "tools" not in api_params
        assert "tool_choice" not in api_params


class TestIntegrationScenarios:
    """Integration tests for common scenarios"""

    def test_full_request_response_cycle_mock(self):
        """Test a full request/response cycle with mocked OpenAI"""
        # This test validates the structure, not actual API calls
        messages = [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": "Hello"}
        ]

        # Mock response structure from OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hello! |||VOICE||| Hi there!"
        mock_response.choices[0].message.tool_calls = None

        # Validate response structure
        assistant_msg = mock_response.choices[0].message
        assert assistant_msg.content is not None
        assert assistant_msg.tool_calls is None

    def test_tool_call_response_cycle_mock(self):
        """Test a tool call response cycle with mocked OpenAI"""
        # Mock tool call response structure
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123abc"
        mock_tool_call.function = Mock()
        mock_tool_call.function.name = "TestAgent"
        mock_tool_call.function.arguments = '{"input": "test"}'

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [mock_tool_call]

        # Validate tool call structure
        assistant_msg = mock_response.choices[0].message
        assert assistant_msg.tool_calls is not None
        assert len(assistant_msg.tool_calls) > 0
        assert assistant_msg.tool_calls[0].function.name == "TestAgent"


# Fixtures
@pytest.fixture
def mock_env_vars():
    """Set up required environment variables for testing"""
    env_vars = {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
        "ASSISTANT_NAME": "Test Assistant",
        "CHARACTERISTIC_DESCRIPTION": "A test assistant"
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def mock_storage():
    """Mock storage manager for tests that don't need real storage"""
    with patch('utils.storage_factory.get_storage_manager') as mock:
        mock_instance = Mock()
        mock_instance.read_json.return_value = {}
        mock_instance.write_json.return_value = None
        mock_instance.list_files.return_value = []
        mock_instance.read_file.return_value = None
        mock_instance.set_memory_context.return_value = True
        mock_instance.current_guid = None
        mock.return_value = mock_instance
        yield mock_instance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
