# MCP Camoufox Scraper Server

A proof-of-concept MCP (Model Context Protocol) server that uses Camoufox for web scraping with JavaScript disabled and network request monitoring.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Poetry (Python dependency manager)
- macOS, Linux, or Windows

### 1. Clone/Download the Project
```bash
git clone <your-repo> mcp-camoufox-scraper
cd mcp-camoufox-scraper
```

### 2. Install Poetry (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies
```bash
poetry install
```

### 4. Verify Setup
```bash
poetry run python setup_verify.py
```

You should see all checks pass:
```
🎉 Setup verification successful!
```

### 5. Run Full Test
```bash
poetry run python test_mcp_server.py
```

You should see:
```
🎉 MCP Server POC is ready!
The server can now be used with MCP clients to scrape websites with JS disabled.
```

## 🔌 Connecting to MCP Clients

### Claude Desktop Integration

1. **Find your Claude Desktop config file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add the server configuration:**
```json
{
  "mcpServers": {
    "camoufox-scraper": {
      "command": "poetry",
      "args": ["run", "python", "/full/path/to/your/mcp-camoufox-scraper/run_server.py"],
      "cwd": "/full/path/to/your/mcp-camoufox-scraper"
    }
  }
}
```

3. **Replace the path** with your actual project directory:
```bash
# Get your full path
pwd
# Copy the output and use it in the config above
```

4. **Restart Claude Desktop** completely (quit and reopen)

5. **Verify connection** by asking Claude:
   > "What MCP servers do you have access to?"

You should see "camoufox-scraper" listed with the available tools.

### Other MCP Clients

For other MCP clients, use this server configuration:
- **Command**: `poetry`
- **Arguments**: `["run", "python", "/path/to/run_server.py"]`
- **Working Directory**: `/path/to/mcp-camoufox-scraper`
- **Communication**: stdio

## 🛠️ Features

- **Dual JavaScript mode**: JavaScript enabled for network monitoring, disabled for clean HTML extraction
- **Network request monitoring**: Capture all XHR/API calls and HTTP requests made during page load
- **Clean HTML extraction**: Get HTML content with JavaScript disabled to avoid dynamic modifications
- **MCP protocol integration**: Works with any MCP client (Claude Desktop, etc.)

## 📋 Available Tools

### 1. `navigate_to_url`
Navigate to a URL with JavaScript enabled to capture network requests and dynamic content.

**Parameters:**
- `url` (required): The URL to navigate to
- `wait_time` (optional): Time to wait after page load in seconds (default: 3)

**Claude Example:**
> "Please navigate to https://example.com and wait 5 seconds"

### 2. `get_page_html`
Extract clean HTML content by re-loading the page with JavaScript disabled.

**Parameters:** None

**Claude Example:**
> "Get the HTML content from the current page"

### 3. `get_network_requests`
Get all captured network requests from the last page navigation.

**Parameters:**
- `filter_type` (optional): Filter by request type ("xhr", "fetch", "all") - default: "all"

**Claude Example:**
> "Show me all the network requests that were captured"

### 4. `close_browser`
Close the browser and cleanup resources.

**Parameters:** None

**Claude Example:**
> "Close the browser to free up resources"

## 💡 Usage Examples

### Basic Web Scraping
```
You: Navigate to https://news.ycombinator.com
Claude: [Uses navigate_to_url tool]
You: Get the HTML content
Claude: [Uses get_page_html tool and analyzes the content]
You: What network requests were made?
Claude: [Uses get_network_requests tool and shows API calls]
```

### API Discovery
```
You: Go to https://httpbin.org/headers and show me what requests it makes
Claude: [Navigates and shows network monitoring results]
```

### Content Analysis
```
You: Navigate to https://example.com and get both the network requests and clean HTML
Claude: [Navigates with JS enabled to capture requests, then extracts HTML with JS disabled]
You: What's the difference between the two modes?
Claude: [Explains that navigation captures dynamic requests while HTML extraction gives clean content]
```

## 🧪 Testing & Verification

### Run Full Test Suite
```bash
poetry run python test_mcp_server.py
```

Expected output:
```
=== Testing MCP Server Tools ===
✓ Navigation successful: Example Domain
✓ HTML extraction successful
✓ Network requests retrieval successful
✓ Complex site navigation successful
✓ Browser closed successfully
🎉 MCP Server POC is ready!
```

### Test Individual Components
```bash
# Test just the Camoufox API
poetry run python test_camoufox_api.py

# Start server manually (for debugging)
poetry run python run_server.py
```

## 🔧 Troubleshooting

### Quick Diagnosis
```bash
# Run the setup verification script first
poetry run python setup_verify.py
```

This will check your Python version, dependencies, project structure, and generate the correct Claude Desktop configuration.

### Server Won't Start
```bash
# Check if dependencies are installed
poetry show mcp camoufox

# Run the test to identify issues
poetry run python test_mcp_server.py
```

### Claude Desktop Connection Issues
1. **Check config file location** - Make sure you're editing the right file
2. **Use absolute paths** - Relative paths won't work
3. **Restart Claude Desktop** completely after config changes
4. **Check Claude's developer tools** for error messages
5. **Verify Python path** - Make sure `python` command works in terminal

### Browser Issues
- **Camoufox download**: First run may take time downloading browser binaries
- **Permission errors**: Make sure the script has execute permissions (`chmod +x run_server.py`)
- **Port conflicts**: Close other browser automation tools if running

### Common Error Messages
- `"No such file or directory"` → Check the path in your config
- `"Permission denied"` → Run `chmod +x run_server.py`
- `"Module not found"` → Run `poetry install`

## 📁 Project Structure

```
mcp-camoufox-scraper/
├── mcp_camoufox_scraper/
│   ├── __init__.py
│   └── server.py              # Main MCP server implementation
├── run_server.py              # CLI runner script  
├── setup_verify.py            # Setup verification & config generator
├── test_mcp_server.py         # Comprehensive test suite
├── test_camoufox_api.py       # Camoufox API validation
├── pyproject.toml            # Project configuration & dependencies
├── poetry.lock               # Locked dependency versions
└── README.md                 # This file
```

## ⚠️ Limitations

- **Dual-context approach**: HTML extraction requires re-navigation with JS disabled
- **Single page**: Only one page can be active at a time  
- **No authentication**: Currently no support for login/auth workflows
- **Limited to HTTP/HTTPS**: No support for other protocols

## 🔒 Security & Privacy

- **No data collection**: Server runs locally, no data sent to external services
- **Controlled JavaScript execution**: JS enabled only when needed for network monitoring
- **Privacy-focused browser**: Camoufox is designed for privacy
- **Local execution**: All scraping happens on your machine

## 🛠️ Development & Extension

### Modifying the Server
1. Edit `mcp_camoufox_scraper/server.py`
2. Test changes: `poetry run python test_mcp_server.py`  
3. Verify MCP compliance with your client

### Adding New Tools
```python
# In server.py, add to _register_tools():
@self.server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    if name == "your_new_tool":
        return await self._your_new_tool(arguments)
```

### Technical Details
- **Browser**: Camoufox (privacy-focused Firefox-based)
- **Protocol**: MCP (Model Context Protocol) 
- **Language**: Python 3.10+ with asyncio
- **Dependencies**: MCP SDK, Camoufox browser automation

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

This is a proof-of-concept project. Feel free to:
- Fork and extend for your use cases
- Submit issues and improvements
- Share your modifications with the community

---

**Happy scraping! 🕷️**