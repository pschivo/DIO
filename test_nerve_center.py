#!/usr/bin/env python3
"""
Test script to verify nerve center can start without errors
"""
import sys
import os
sys.path.append('/home/z/my-project/components/nerve-center')

try:
    # Test importing the main module
    import main
    print("✅ Nerve Center main.py imports successfully")
    
    # Test key functions exist
    assert hasattr(main, 'app'), "FastAPI app not found"
    assert hasattr(main, 'initialize_caches'), "initialize_caches function not found"
    assert hasattr(main, 'backup_database'), "backup_database function not found"
    assert hasattr(main, 'restore_database'), "restore_database function not found"
    
    print("✅ All required functions are present")
    print("✅ Nerve Center code structure is valid")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"❌ Assertion error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print("\n🎉 Nerve Center verification completed successfully!")