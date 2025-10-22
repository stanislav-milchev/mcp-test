#!/usr/bin/env python3
"""
Setup verification script for MCP Camoufox Scraper.
Run this to verify your installation is working correctly.
"""

import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 10):
        print("❌ Python 3.10+ required. Current version:", f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_poetry():
    """Check if Poetry is installed and working"""
    try:
        result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
        else:
            print("❌ Poetry not working properly")
            return False
    except FileNotFoundError:
        print("❌ Poetry not installed")
        print("📦 Install Poetry: https://python-poetry.org/docs/#installation")
        return False
    except Exception as e:
        print(f"❌ Error checking Poetry: {e}")
        return False

def check_dependencies():
    """Check if project dependencies are installed via Poetry"""
    try:
        # Check if poetry.lock exists
        if not Path("poetry.lock").exists():
            print("❌ poetry.lock not found")
            print("📦 Run: poetry install")
            return False
        
        # Try to show installed packages
        result = subprocess.run(['poetry', 'run', 'python', '-c', 
                               'import mcp, camoufox; print("Dependencies available")'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All dependencies installed via Poetry")
            
            # Get package versions
            try:
                mcp_result = subprocess.run(['poetry', 'show', 'mcp'], capture_output=True, text=True)
                camoufox_result = subprocess.run(['poetry', 'show', 'camoufox'], capture_output=True, text=True)
                
                if mcp_result.returncode == 0:
                    mcp_version = mcp_result.stdout.split('\n')[1].split()[1] if mcp_result.stdout else 'unknown'
                    print(f"  • mcp version: {mcp_version}")
                
                if camoufox_result.returncode == 0:
                    camoufox_version = camoufox_result.stdout.split('\n')[1].split()[1] if camoufox_result.stdout else 'unknown'
                    print(f"  • camoufox version: {camoufox_version}")
                    
            except Exception:
                pass  # Version info is optional
                
            return True
        else:
            print("❌ Dependencies not properly installed")
            print("📦 Run: poetry install")
            return False
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        print("📦 Run: poetry install")
        return False

def check_project_structure():
    """Check if project files are in the right place"""
    required_files = [
        'mcp_camoufox_scraper/__init__.py',
        'mcp_camoufox_scraper/server.py', 
        'run_server.py',
        'test_mcp_server.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    return len(missing_files) == 0

def test_imports():
    """Test if we can import the server using Poetry"""
    try:
        # Test imports using Poetry environment
        result = subprocess.run([
            'poetry', 'run', 'python', '-c',
            'from mcp_camoufox_scraper.server import CamoufoxMCPServer; '
            'server = CamoufoxMCPServer(); '
            'print("✅ Server imports and instantiation successful")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Server imports successfully")
            print("✅ Server instantiation successful")
            return True
        else:
            print(f"❌ Import/instantiation failed: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Import/instantiation failed: {e}")
        return False

def generate_claude_config():
    """Generate Claude Desktop configuration snippet"""
    current_dir = Path.cwd().absolute()
    run_server_path = current_dir / "run_server.py"
    
    config = {
        "mcpServers": {
            "camoufox-scraper": {
                "command": "poetry",
                "args": ["run", "python", str(run_server_path)],
                "cwd": str(current_dir)
            }
        }
    }
    
    print("\n📋 Claude Desktop Configuration:")
    print("Add this to your claude_desktop_config.json:")
    print(json.dumps(config, indent=2))
    
    # Show config file locations
    print("\n📁 Config file locations:")
    print("• macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("• Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("• Linux: ~/.config/Claude/claude_desktop_config.json")

def main():
    """Run all verification checks"""
    print("🔍 MCP Camoufox Scraper - Setup Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 4
    
    # Check 1: Python version
    print("\n1. Checking Python version...")
    if check_python_version():
        checks_passed += 1
    
    # Check 2: Dependencies
    print("\n2. Checking dependencies...")
    if check_dependencies():
        checks_passed += 1
    
    # Check 3: Project structure
    print("\n3. Checking project structure...")
    if check_project_structure():
        checks_passed += 1
    
    # Check 4: Imports
    print("\n4. Testing imports...")
    if test_imports():
        checks_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Setup verification successful!")
        print("\n🚀 Next steps:")
        print("1. Run the full test: python test_mcp_server.py")
        print("2. Add the configuration to Claude Desktop (see below)")
        print("3. Restart Claude Desktop completely")
        print("4. Ask Claude: 'What MCP servers do you have access to?'")
        
        generate_claude_config()
        
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())