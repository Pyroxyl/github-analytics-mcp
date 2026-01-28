"""基本 import 測試腳本"""

import sys
sys.path.insert(0, "src")

try:
    import github_client
    print("✓ github_client imported successfully")

    import server
    print("✓ server imported successfully")

    print("\nAll imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
