"""MCP Server 測試腳本"""

import os
import sys

# 設定假的 GITHUB_TOKEN 來測試錯誤處理
os.environ["GITHUB_TOKEN"] = "test_token_for_error_handling"

# 將 src 加入路徑
sys.path.insert(0, "src")

try:
    import server
    print("MCP Server module loaded successfully")
    print()
    print("Available tools:")
    for tool in server.TOOLS:
        print(f"  - {tool.name}: {tool.description[:50]}...")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
