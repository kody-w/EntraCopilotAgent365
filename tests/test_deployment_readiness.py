"""
Deployment Readiness Tests

These tests validate that the application is ready for deployment.
Run before every deployment to catch configuration and code issues.

Usage:
    pytest tests/test_deployment_readiness.py -v

Or use the run_pre_deployment_tests.py script:
    python run_pre_deployment_tests.py
"""

import pytest
import os
import sys
import json
import importlib
from pathlib import Path
from unittest.mock import patch, Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRequiredFiles:
    """Verify all required files exist"""

    def test_function_app_exists(self):
        """Main function app file must exist"""
        assert (project_root / "function_app.py").exists()

    def test_requirements_exists(self):
        """Requirements file must exist"""
        assert (project_root / "requirements.txt").exists()

    def test_host_json_exists(self):
        """Host configuration must exist"""
        assert (project_root / "host.json").exists()

    def test_basic_agent_exists(self):
        """Basic agent base class must exist"""
        assert (project_root / "agents" / "basic_agent.py").exists()

    def test_storage_utils_exist(self):
        """Storage utilities must exist"""
        assert (project_root / "utils" / "storage_factory.py").exists()
        assert (project_root / "utils" / "azure_file_storage.py").exists()
        assert (project_root / "utils" / "local_file_storage.py").exists()
        assert (project_root / "utils" / "environment.py").exists()


class TestRequiredDependencies:
    """Verify all required dependencies are installed"""

    def test_azure_functions_import(self):
        """Azure Functions must be importable"""
        import azure.functions
        assert azure.functions is not None

    def test_openai_import(self):
        """OpenAI library must be importable"""
        import openai
        assert openai is not None

    def test_azure_identity_import(self):
        """Azure Identity must be importable"""
        import azure.identity
        assert azure.identity is not None

    def test_azure_storage_import(self):
        """Azure Storage must be importable"""
        import azure.storage.fileshare
        import azure.storage.blob
        assert azure.storage.fileshare is not None
        assert azure.storage.blob is not None


class TestCodeSyntax:
    """Verify code files have valid syntax"""

    def test_function_app_syntax(self):
        """function_app.py must have valid syntax"""
        try:
            import function_app
            assert function_app is not None
        except SyntaxError as e:
            pytest.fail(f"Syntax error in function_app.py: {e}")

    def test_agents_syntax(self):
        """All agent files must have valid syntax"""
        agents_dir = project_root / "agents"
        for agent_file in agents_dir.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue
            try:
                with open(agent_file, 'r') as f:
                    compile(f.read(), agent_file, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {agent_file.name}: {e}")

    def test_utils_syntax(self):
        """All utility files must have valid syntax"""
        utils_dir = project_root / "utils"
        for util_file in utils_dir.glob("*.py"):
            if util_file.name.startswith("__"):
                continue
            try:
                with open(util_file, 'r') as f:
                    compile(f.read(), util_file, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {util_file.name}: {e}")


class TestOpenAIApiFormat:
    """Verify OpenAI API calls use correct format"""

    def test_tools_format_not_functions_format(self):
        """API calls should use 'tools' not deprecated 'functions'"""
        function_app_path = project_root / "function_app.py"
        with open(function_app_path, 'r') as f:
            content = f.read()

        # Should NOT have the old format
        assert 'functions=self.get_agent_metadata()' not in content, \
            "Code uses deprecated 'functions' parameter. Should use 'tools' format."
        assert 'function_call="auto"' not in content, \
            "Code uses deprecated 'function_call' parameter. Should use 'tool_choice' format."

        # Should have the new format
        assert 'tools=' in content or '"tools"' in content, \
            "Code should use 'tools' parameter for function calling."
        assert 'tool_choice' in content, \
            "Code should use 'tool_choice' parameter for function calling."

    def test_tool_calls_response_handling(self):
        """Response handling should check tool_calls not function_call"""
        function_app_path = project_root / "function_app.py"
        with open(function_app_path, 'r') as f:
            content = f.read()

        # Should use tool_calls
        assert 'tool_calls' in content, \
            "Code should check for 'tool_calls' in response."

        # Should NOT check for deprecated function_call (except in comments)
        lines = [l for l in content.split('\n') if not l.strip().startswith('#')]
        non_comment_content = '\n'.join(lines)
        assert 'assistant_msg.function_call' not in non_comment_content, \
            "Code should not use deprecated 'function_call' attribute."


class TestAgentMetadataStructure:
    """Verify agent metadata is properly structured for OpenAI tools API"""

    def test_context_memory_agent_metadata(self):
        """ContextMemoryAgent must have valid metadata"""
        with patch('utils.storage_factory.get_storage_manager'):
            from agents.context_memory_agent import ContextMemoryAgent
            agent = ContextMemoryAgent()

            metadata = agent.metadata
            assert "name" in metadata
            assert "description" in metadata
            assert "parameters" in metadata
            assert metadata["parameters"]["type"] == "object"

    def test_agent_metadata_converts_to_tools(self):
        """All agent metadata must convert to valid tools format"""
        with patch('utils.storage_factory.get_storage_manager'):
            from agents.context_memory_agent import ContextMemoryAgent
            agent = ContextMemoryAgent()

            # Convert to tools format
            tool = {"type": "function", "function": agent.metadata}

            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]


class TestErrorHandling:
    """Verify error handling is properly implemented"""

    def test_retry_logic_exists(self):
        """Retry logic should be implemented for API calls"""
        function_app_path = project_root / "function_app.py"
        with open(function_app_path, 'r') as f:
            content = f.read()

        assert 'max_retries' in content
        assert 'retry_count' in content

    def test_error_logging_exists(self):
        """Error logging should be implemented"""
        function_app_path = project_root / "function_app.py"
        with open(function_app_path, 'r') as f:
            content = f.read()

        assert 'logging.error' in content
        assert 'Error Type:' in content or 'error_type' in content


class TestConfigurationValidation:
    """Verify configuration files are valid"""

    def test_host_json_valid(self):
        """host.json must be valid JSON"""
        host_json_path = project_root / "host.json"
        with open(host_json_path, 'r') as f:
            try:
                config = json.load(f)
                assert "version" in config
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in host.json: {e}")

    def test_requirements_not_empty(self):
        """requirements.txt must have dependencies"""
        requirements_path = project_root / "requirements.txt"
        with open(requirements_path, 'r') as f:
            content = f.read().strip()
            assert len(content) > 0
            # Check for critical dependencies
            assert 'azure-functions' in content
            assert 'openai' in content


class TestLocalSettingsTemplate:
    """Verify local settings template is properly configured"""

    def test_template_exists(self):
        """Template file must exist"""
        template_path = project_root / "local.settings.template.json"
        assert template_path.exists(), "local.settings.template.json is required"

    def test_template_has_required_keys(self):
        """Template must have all required configuration keys"""
        template_path = project_root / "local.settings.template.json"

        with open(template_path, 'r') as f:
            config = json.load(f)

        values = config.get("Values", {})
        required_keys = [
            "FUNCTIONS_WORKER_RUNTIME",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "AZURE_STORAGE_ACCOUNT_NAME",
            "AZURE_FILES_SHARE_NAME",
        ]

        for key in required_keys:
            assert key in values, f"Template missing required key: {key}"


class TestImportChain:
    """Verify import chain works correctly"""

    def test_function_app_imports(self):
        """function_app.py must import without errors"""
        # This test validates the entire import chain
        try:
            # We need to mock the storage to avoid Azure connection errors
            with patch('utils.storage_factory.get_storage_manager'):
                # Force reimport
                if 'function_app' in sys.modules:
                    del sys.modules['function_app']

                import function_app
                assert hasattr(function_app, 'main')
                assert hasattr(function_app, 'Assistant')
        except ImportError as e:
            pytest.fail(f"Import error in function_app.py: {e}")

    def test_agent_imports(self):
        """All agents must import without errors"""
        with patch('utils.storage_factory.get_storage_manager'):
            try:
                from agents.basic_agent import BasicAgent
                from agents.context_memory_agent import ContextMemoryAgent
                assert BasicAgent is not None
                assert ContextMemoryAgent is not None
            except ImportError as e:
                pytest.fail(f"Import error in agents: {e}")


class TestCriticalFunctions:
    """Verify critical functions exist and are callable"""

    def test_ensure_string_content_exists(self):
        """ensure_string_content must exist"""
        from function_app import ensure_string_content
        assert callable(ensure_string_content)

    def test_build_cors_response_exists(self):
        """build_cors_response must exist"""
        from function_app import build_cors_response
        assert callable(build_cors_response)

    def test_load_agents_from_folder_exists(self):
        """load_agents_from_folder must exist"""
        from function_app import load_agents_from_folder
        assert callable(load_agents_from_folder)


def run_all_deployment_tests():
    """Run all deployment readiness tests and return results"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


if __name__ == "__main__":
    # Run tests
    exit_code = pytest.main([__file__, "-v"])
    sys.exit(exit_code)
