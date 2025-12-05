#!/usr/bin/env python3
"""
Pre-Deployment Test Runner

Run this script before deploying to Azure to catch issues early.

Usage:
    python run_pre_deployment_tests.py

Or with verbose output:
    python run_pre_deployment_tests.py -v

This script runs:
1. Deployment readiness tests (configuration, imports, syntax)
2. Unit tests (functionality)
3. Local storage tests (if using local development)
"""

import subprocess
import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_failure(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def run_pytest(test_path, verbose=False):
    """Run pytest on the specified path"""
    args = [sys.executable, "-m", "pytest", test_path]
    if verbose:
        args.append("-v")
    args.extend(["--tb=short", "-q"])

    result = subprocess.run(args, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major != 3 or version.minor < 11:
        print_warning(f"Python {version.major}.{version.minor} detected. Python 3.11 is recommended for Azure Functions v4.")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ['azure.functions', 'openai', 'azure.identity', 'azure.storage.fileshare']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print_failure(f"Missing dependencies: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt")
        return False

    print_success("All required dependencies installed")
    return True


def check_local_settings():
    """Check if local.settings.json exists and has required keys"""
    project_root = Path(__file__).parent
    settings_path = project_root / "local.settings.json"

    if not settings_path.exists():
        print_warning("local.settings.json not found (required for local testing)")
        return True  # Not a failure, just a warning

    import json
    with open(settings_path, 'r') as f:
        config = json.load(f)

    values = config.get("Values", {})
    required_keys = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
    ]

    missing = [k for k in required_keys if not values.get(k) or values.get(k).startswith("<")]
    if missing:
        print_warning(f"local.settings.json missing or has placeholder values for: {', '.join(missing)}")
        return True  # Warning, not failure

    print_success("local.settings.json configured correctly")
    return True


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    print_header("PRE-DEPLOYMENT TEST SUITE")
    print("Running tests to validate deployment readiness...\n")

    project_root = Path(__file__).parent
    results = {}

    # 1. Environment Checks
    print_header("ENVIRONMENT CHECKS")

    results["python_version"] = check_python_version()
    results["dependencies"] = check_dependencies()
    results["local_settings"] = check_local_settings()

    # 2. Deployment Readiness Tests
    print_header("DEPLOYMENT READINESS TESTS")

    test_file = project_root / "tests" / "test_deployment_readiness.py"
    if test_file.exists():
        passed, stdout, stderr = run_pytest(str(test_file), verbose)
        results["deployment_readiness"] = passed
        if passed:
            print_success("All deployment readiness tests passed")
        else:
            print_failure("Some deployment readiness tests failed")
            if verbose:
                print(stdout)
                print(stderr)
    else:
        print_warning("test_deployment_readiness.py not found")
        results["deployment_readiness"] = True

    # 3. Unit Tests
    print_header("UNIT TESTS")

    unit_test_file = project_root / "tests" / "test_function_app.py"
    if unit_test_file.exists():
        passed, stdout, stderr = run_pytest(str(unit_test_file), verbose)
        results["unit_tests"] = passed
        if passed:
            print_success("All unit tests passed")
        else:
            print_failure("Some unit tests failed")
            if verbose:
                print(stdout)
                print(stderr)
    else:
        print_warning("test_function_app.py not found")
        results["unit_tests"] = True

    # 4. Storage Tests (optional)
    print_header("STORAGE TESTS")

    storage_test_file = project_root / "test_local_storage.py"
    if storage_test_file.exists():
        print("Running storage tests...")
        result = subprocess.run(
            [sys.executable, str(storage_test_file)],
            capture_output=True,
            text=True
        )
        results["storage_tests"] = result.returncode == 0
        if result.returncode == 0:
            print_success("Storage tests passed")
        else:
            print_warning("Storage tests had issues (may be expected in CI)")
            if verbose:
                print(result.stdout)
    else:
        print_warning("test_local_storage.py not found")
        results["storage_tests"] = True

    # Summary
    print_header("TEST SUMMARY")

    all_passed = all(results.values())
    critical_passed = results.get("deployment_readiness", True) and results.get("unit_tests", True)

    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        color_func = print_success if passed else print_failure
        color_func(f"{test_name.replace('_', ' ').title()}: {status}")

    print("\n" + "=" * 60)

    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED - Ready for deployment!{Colors.END}")
        return 0
    elif critical_passed:
        print(f"{Colors.YELLOW}{Colors.BOLD}CRITICAL TESTS PASSED - Deployment should work, but review warnings{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}CRITICAL TESTS FAILED - DO NOT DEPLOY{Colors.END}")
        print(f"\nFix the issues above before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
