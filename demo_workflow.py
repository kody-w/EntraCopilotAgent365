#!/usr/bin/env python3
"""
🎭 Workflow Runner Demo Script
================================

This script demonstrates the power of the Workflow Runner Agent and IQ Booster system.

Run modes:
  python demo_workflow.py              # Interactive menu
  python demo_workflow.py --test       # Run all tests
  python demo_workflow.py --live       # Execute actual IQ boost (PRODUCTION!)
  python demo_workflow.py --api        # Test via HTTP API

Requirements:
  - Azure CLI logged in (az login)
  - Virtual environment activated
  - For --api mode: func start running
"""

import os
import sys
import json
import subprocess
import time
import requests
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_step(text: str):
    print(f"{Colors.CYAN}▶ {text}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.ENDC}")

def print_code(text: str):
    print(f"{Colors.BLUE}{text}{Colors.ENDC}")

# ============================================================================
# Test Functions
# ============================================================================

def test_imports():
    """Test that all agents can be imported"""
    print_step("Testing agent imports...")

    try:
        from agents.basic_agent import BasicAgent
        print_success("BasicAgent imported")

        from agents.iq_booster_agent import IQBoosterAgent
        agent = IQBoosterAgent()
        print_success(f"IQBoosterAgent imported: {agent.name}")

        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()
        print_success(f"WorkflowRunnerAgent imported: {agent.name}")

        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        return False

def test_workflow_list():
    """Test listing available workflows"""
    print_step("Testing workflow listing...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(action='list')
        print_code(result)

        if 'iq_boost_workflow' in result:
            print_success("Workflow list works!")
            return True
        else:
            print_error("Expected workflow not found")
            return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_workflow_describe():
    """Test describing a workflow"""
    print_step("Testing workflow description...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(action='describe', workflow_name='iq_boost_workflow')
        print_code(result[:1500] + "..." if len(result) > 1500 else result)

        print_success("Workflow describe works!")
        return True
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_workflow_validate():
    """Test workflow validation"""
    print_step("Testing workflow validation...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(action='validate', workflow_name='iq_boost_workflow')
        print_code(result)

        if 'valid' in result.lower():
            print_success("Workflow validation works!")
            return True
        else:
            print_error("Validation returned unexpected result")
            return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_workflow_dry_run():
    """Test dry-run mode"""
    print_step("Testing workflow dry-run...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(
            action='dry_run',
            workflow_name='iq_boost_workflow',
            variables={
                'function_app_name': 'copilot365-4ovzneuimhd2g',
                'resource_group': 'rappai'
            }
        )
        print_code(result[:2000] + "..." if len(result) > 2000 else result)

        print_success("Workflow dry-run works!")
        return True
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_iq_booster_status():
    """Test IQ Booster status action"""
    print_step("Testing IQ Booster status...")

    try:
        from agents.iq_booster_agent import IQBoosterAgent
        agent = IQBoosterAgent()

        result = agent.perform(action='status')
        print_code(result)

        print_success("IQ Booster status works!")
        return True
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_iq_booster_discover():
    """Test IQ Booster resource discovery"""
    print_step("Testing IQ Booster resource discovery...")

    try:
        from agents.iq_booster_agent import IQBoosterAgent
        agent = IQBoosterAgent()

        result = agent.perform(action='discover_resources')
        print_code(result[:2000] + "..." if len(result) > 2000 else result)

        print_success("IQ Booster discovery works!")
        return True
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def test_azure_cli():
    """Test Azure CLI connectivity"""
    print_step("Testing Azure CLI...")

    try:
        result = subprocess.run(
            ['az', 'account', 'show', '--query', '{name:name, user:user.name}', '-o', 'json'],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            account = json.loads(result.stdout)
            print_success(f"Azure CLI connected as: {account.get('user', 'Unknown')}")
            print_info(f"Subscription: {account.get('name', 'Unknown')}")
            return True
        else:
            print_error("Azure CLI not logged in")
            print_info("Run: az login")
            return False
    except Exception as e:
        print_error(f"Azure CLI test failed: {e}")
        return False

# ============================================================================
# Live Execution
# ============================================================================

def run_live_boost():
    """Execute the actual IQ Boost workflow (PRODUCTION!)"""
    print_header("🚀 LIVE IQ BOOST EXECUTION")

    print(f"{Colors.RED}{Colors.BOLD}")
    print("⚠️  WARNING: This will modify PRODUCTION settings!")
    print("    - Updates local.settings.json")
    print("    - Updates Azure Function App configuration")
    print(f"{Colors.ENDC}")

    confirm = input("\nType 'BOOST' to confirm: ")
    if confirm != 'BOOST':
        print_info("Cancelled.")
        return

    print_step("Executing IQ Boost workflow...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(
            action='run',
            workflow_name='iq_boost_workflow',
            variables={
                'function_app_name': 'copilot365-4ovzneuimhd2g',
                'resource_group': 'rappai'
            }
        )

        print("\n" + result)

    except Exception as e:
        print_error(f"Execution failed: {e}")

def run_live_iq_boost():
    """Execute IQ Boost via the IQBoosterAgent directly"""
    print_header("🚀 LIVE IQ BOOST (Direct Agent)")

    print(f"{Colors.RED}{Colors.BOLD}")
    print("⚠️  WARNING: This will modify PRODUCTION settings!")
    print(f"{Colors.ENDC}")

    confirm = input("\nType 'BOOST' to confirm: ")
    if confirm != 'BOOST':
        print_info("Cancelled.")
        return

    print_step("Executing IQ Boost via agent...")

    try:
        from agents.iq_booster_agent import IQBoosterAgent
        agent = IQBoosterAgent()

        result = agent.perform(action='boost')
        print("\n" + result)

    except Exception as e:
        print_error(f"Execution failed: {e}")

# ============================================================================
# API Testing
# ============================================================================

def test_api_call():
    """Test via HTTP API"""
    print_header("🌐 API Test")

    # Configuration
    API_URL = "https://copilot365-4ovzneuimhd2g.azurewebsites.net/api/businessinsightbot_function"
    API_KEY = "REDACTED_API_KEY"

    LOCAL_URL = "http://localhost:7071/api/businessinsightbot_function"

    print_info("Choose endpoint:")
    print("  1. Local (localhost:7071)")
    print("  2. Production (Azure)")

    choice = input("\nChoice [1/2]: ").strip()

    url = LOCAL_URL if choice == '1' else API_URL
    headers = {"Content-Type": "application/json"}
    if choice == '2':
        headers["x-functions-key"] = API_KEY

    print_info(f"Using: {url}")

    # Test prompts
    prompts = [
        "What's your current status?",
        "List available workflows",
        "Show me your IQ booster capabilities",
        "Discover my Azure OpenAI resources"
    ]

    print_info("\nSelect a test prompt:")
    for i, p in enumerate(prompts, 1):
        print(f"  {i}. {p}")
    print(f"  {len(prompts)+1}. Custom prompt")

    choice = input("\nChoice: ").strip()

    try:
        idx = int(choice) - 1
        if idx < len(prompts):
            prompt = prompts[idx]
        else:
            prompt = input("Enter custom prompt: ")
    except:
        prompt = prompts[0]

    print_step(f"Sending: {prompt}")

    payload = {
        "user_input": prompt,
        "conversation_history": []
    }

    try:
        start = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        elapsed = time.time() - start

        print_info(f"Response time: {elapsed:.2f}s")
        print_info(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_success("Response received!")
            print("\n" + "="*60)
            print(data.get('assistant_response', 'No response'))
            print("="*60)

            if data.get('agent_logs'):
                print(f"\n{Colors.YELLOW}Agent Logs:{Colors.ENDC}")
                print(data.get('agent_logs'))
        else:
            print_error(f"API error: {response.text}")

    except requests.exceptions.ConnectionError:
        print_error("Connection failed. Is the function running?")
        print_info("Start locally with: func start")
    except Exception as e:
        print_error(f"Request failed: {e}")

# ============================================================================
# Demo Scenarios
# ============================================================================

def demo_workflow_creation():
    """Demonstrate creating a custom workflow"""
    print_header("📝 Creating Custom Workflow")

    print_info("This demonstrates how to create a custom workflow.")

    # Example workflow
    workflow = {
        "name": "Demo Workflow",
        "description": "A simple demo workflow",
        "version": "1.0",
        "variables": {
            "greeting": {"type": "string", "default": "Hello"}
        },
        "steps": [
            {
                "id": "step1",
                "name": "Check Azure CLI",
                "action": "az_command",
                "command": "az account show --query '{name:name}' -o json",
                "outputs": {"account_name": "$.name"}
            },
            {
                "id": "step2",
                "name": "Generate Greeting",
                "action": "template",
                "template": "${greeting}, you are logged into ${step1.account_name}!",
                "outputs": {"message": "$"}
            }
        ],
        "on_complete": {
            "action": "return",
            "value": "${step2.message}"
        }
    }

    print_code(json.dumps(workflow, indent=2))

    print_step("\nRunning demo workflow...")

    try:
        from agents.workflow_runner_agent import WorkflowRunnerAgent
        agent = WorkflowRunnerAgent()

        result = agent.perform(
            action='run',
            workflow_json=workflow,
            variables={'greeting': 'Welcome'}
        )

        print("\n" + result)
        print_success("Custom workflow executed!")

    except Exception as e:
        print_error(f"Failed: {e}")

# ============================================================================
# Main Menu
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print_header("🧪 Running All Tests")

    tests = [
        ("Agent Imports", test_imports),
        ("Azure CLI", test_azure_cli),
        ("Workflow List", test_workflow_list),
        ("Workflow Describe", test_workflow_describe),
        ("Workflow Validate", test_workflow_validate),
        ("Workflow Dry-Run", test_workflow_dry_run),
        ("IQ Booster Status", test_iq_booster_status),
        ("IQ Booster Discover", test_iq_booster_discover),
    ]

    results = []

    for name, test_func in tests:
        print_header(f"Test: {name}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((name, False))

        print()  # Spacing

    # Summary
    print_header("📊 Test Summary")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, success in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if success else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
        print(f"  {status}  {name}")

    print(f"\n  {Colors.BOLD}Results: {passed}/{total} passed{Colors.ENDC}")

    if passed == total:
        print_success("\n🎉 All tests passed!")
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")

def interactive_menu():
    """Interactive menu"""
    while True:
        print_header("🎭 Workflow Runner Demo")

        print(f"""
{Colors.CYAN}Testing:{Colors.ENDC}
  1. Run all tests
  2. Test agent imports
  3. Test Azure CLI connection

{Colors.CYAN}Workflow Runner:{Colors.ENDC}
  4. List workflows
  5. Describe workflow
  6. Validate workflow
  7. Dry-run workflow

{Colors.CYAN}IQ Booster:{Colors.ENDC}
  8. Show status
  9. Discover resources
  10. Dry-run boost

{Colors.CYAN}Live Execution:{Colors.ENDC}
  11. {Colors.RED}Execute IQ Boost (PRODUCTION!){Colors.ENDC}
  12. {Colors.RED}Execute via Workflow Runner (PRODUCTION!){Colors.ENDC}

{Colors.CYAN}API Testing:{Colors.ENDC}
  13. Test via HTTP API

{Colors.CYAN}Demos:{Colors.ENDC}
  14. Demo custom workflow creation

{Colors.YELLOW}0. Exit{Colors.ENDC}
""")

        choice = input("Select option: ").strip()

        if choice == '0':
            print_info("Goodbye!")
            break
        elif choice == '1':
            run_all_tests()
        elif choice == '2':
            test_imports()
        elif choice == '3':
            test_azure_cli()
        elif choice == '4':
            test_workflow_list()
        elif choice == '5':
            test_workflow_describe()
        elif choice == '6':
            test_workflow_validate()
        elif choice == '7':
            test_workflow_dry_run()
        elif choice == '8':
            test_iq_booster_status()
        elif choice == '9':
            test_iq_booster_discover()
        elif choice == '10':
            from agents.iq_booster_agent import IQBoosterAgent
            agent = IQBoosterAgent()
            result = agent.perform(action='boost', dry_run=True)
            print(result)
        elif choice == '11':
            run_live_iq_boost()
        elif choice == '12':
            run_live_boost()
        elif choice == '13':
            test_api_call()
        elif choice == '14':
            demo_workflow_creation()
        else:
            print_error("Invalid option")

        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Parse command line args
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ('--test', '-t'):
            run_all_tests()
        elif arg in ('--live', '-l'):
            run_live_iq_boost()
        elif arg in ('--api', '-a'):
            test_api_call()
        elif arg in ('--help', '-h'):
            print(__doc__)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage")
    else:
        interactive_menu()
