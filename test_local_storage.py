#!/usr/bin/env python3
"""
Test script to verify environment-aware storage system works correctly.

This script tests:
1. Environment detection
2. Storage manager initialization
3. Basic read/write operations
4. Memory context switching
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_detection():
    """Test environment detection functions"""
    print("\n" + "="*60)
    print("TEST 1: Environment Detection")
    print("="*60)

    from utils.environment import (
        is_running_in_azure,
        should_use_azure_storage,
        get_local_storage_path
    )

    azure_env = is_running_in_azure()
    use_azure = should_use_azure_storage()
    local_path = get_local_storage_path()

    print(f"Running in Azure: {azure_env}")
    print(f"Should use Azure storage: {use_azure}")
    print(f"Local storage path: {local_path}")

    return True

def test_storage_initialization():
    """Test storage manager initialization"""
    print("\n" + "="*60)
    print("TEST 2: Storage Manager Initialization")
    print("="*60)

    try:
        from utils.storage_factory import get_storage_manager

        storage = get_storage_manager()
        storage_type = type(storage).__name__

        print(f"Storage manager type: {storage_type}")
        print(f"Base path: {getattr(storage, 'base_path', 'N/A')}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to initialize storage: {e}")
        return False

def test_memory_operations():
    """Test basic memory read/write operations"""
    print("\n" + "="*60)
    print("TEST 3: Memory Operations")
    print("="*60)

    try:
        from utils.storage_factory import get_storage_manager

        storage = get_storage_manager()

        # Test shared memory
        print("\n[Shared Memory]")
        storage.set_memory_context(None)

        # Write test data
        test_data = {
            "test": True,
            "message": "Test memory write",
            "memories": [
                {
                    "id": "test_001",
                    "type": "fact",
                    "content": "This is a test memory"
                }
            ]
        }

        print("Writing test data...")
        storage.write_json(test_data)

        # Read it back
        print("Reading test data...")
        data = storage.read_json()

        if data.get("test") == True:
            print("✓ Shared memory write/read successful")
        else:
            print("✗ Shared memory data mismatch")
            return False

        # Test user-specific memory
        print("\n[User-Specific Memory]")
        test_guid = "c0p110t0-aaaa-bbbb-cccc-123456789abc"

        context_set = storage.set_memory_context(test_guid)
        print(f"Set memory context for GUID: {test_guid}")
        print(f"Context set successfully: {context_set}")

        # Write user-specific data
        user_data = {
            "user_guid": test_guid,
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }

        print("Writing user-specific data...")
        storage.write_json(user_data)

        # Read it back
        print("Reading user-specific data...")
        data = storage.read_json()

        if data.get("user_guid") == test_guid:
            print("✓ User-specific memory write/read successful")
        else:
            print("✗ User-specific memory data mismatch")
            return False

        return True

    except Exception as e:
        print(f"ERROR: Memory operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file read/write operations"""
    print("\n" + "="*60)
    print("TEST 4: File Operations")
    print("="*60)

    try:
        from utils.storage_factory import get_storage_manager

        storage = get_storage_manager()

        # Test directory creation
        print("\n[Directory Operations]")
        test_dir = "test_agents"
        result = storage.ensure_directory_exists(test_dir)
        print(f"Create directory '{test_dir}': {result}")

        # Test file write
        print("\n[File Write]")
        test_content = """
from agents.basic_agent import BasicAgent

class TestAgent(BasicAgent):
    def __init__(self):
        self.name = 'Test'
        self.metadata = {"name": "Test", "description": "Test agent"}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return "Test successful!"
"""

        write_result = storage.write_file(test_dir, 'test_agent.py', test_content)
        print(f"Write file 'test_agent.py': {write_result}")

        # Test file read
        print("\n[File Read]")
        read_content = storage.read_file(test_dir, 'test_agent.py')

        if read_content and "TestAgent" in read_content:
            print("✓ File read successful")
        else:
            print("✗ File read failed or content mismatch")
            return False

        # Test file exists
        print("\n[File Existence Check]")
        exists = storage.file_exists(test_dir, 'test_agent.py')
        print(f"File exists: {exists}")

        # Test list files
        print("\n[List Files]")
        files = storage.list_files(test_dir)
        print(f"Files in '{test_dir}': {[f.name for f in files]}")

        # Test file properties
        print("\n[File Properties]")
        props = storage.get_file_properties(test_dir, 'test_agent.py')
        if props:
            print(f"File size: {props['size']} bytes")
            print(f"Last modified: {props['last_modified']}")

        # Test file deletion
        print("\n[File Deletion]")
        delete_result = storage.delete_file(test_dir, 'test_agent.py')
        print(f"Delete file: {delete_result}")

        return True

    except Exception as e:
        print(f"ERROR: File operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_location():
    """Verify storage location and contents"""
    print("\n" + "="*60)
    print("TEST 5: Storage Location Verification")
    print("="*60)

    try:
        from utils.environment import get_local_storage_path, should_use_azure_storage

        if should_use_azure_storage():
            print("Using Azure storage - skipping local file verification")
            return True

        local_path = Path(get_local_storage_path())

        print(f"\nLocal storage path: {local_path}")
        print(f"Path exists: {local_path.exists()}")

        if local_path.exists():
            print("\nDirectory structure:")
            for item in sorted(local_path.rglob('*')):
                rel_path = item.relative_to(local_path)
                if item.is_file():
                    print(f"  📄 {rel_path} ({item.stat().st_size} bytes)")
                else:
                    print(f"  📁 {rel_path}/")

        return True

    except Exception as e:
        print(f"ERROR: Storage location verification failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ENVIRONMENT-AWARE STORAGE TEST SUITE")
    print("="*60)

    tests = [
        ("Environment Detection", test_environment_detection),
        ("Storage Initialization", test_storage_initialization),
        ("Memory Operations", test_memory_operations),
        ("File Operations", test_file_operations),
        ("Storage Location", test_storage_location),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
