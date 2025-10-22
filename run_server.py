#!/usr/bin/env python3
"""
CLI runner for the MCP Camoufox Scraper server.
This makes it easy to start the server from the command line.
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_camoufox_scraper.server import main

if __name__ == "__main__":
    print("🚀 Starting MCP Camoufox Scraper Server...")
    print("The server will communicate via stdio for MCP clients.")
    print("To stop the server, press Ctrl+C")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)