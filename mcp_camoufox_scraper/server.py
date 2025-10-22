#!/usr/bin/env python3
"""
MCP server POC using Camoufox for web scraping with network monitoring.
This server provides tools to navigate websites with JavaScript disabled
and capture both HTML content and network requests.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp import types

from camoufox import AsyncCamoufox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CamoufoxMCPServer:
    def __init__(self):
        self.server = Server("camoufox-scraper")
        self.camoufox: Optional[AsyncCamoufox] = None
        self.browser = None
        self.context = None
        self.page = None
        self.network_requests: List[Dict[str, Any]] = []

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="navigate_to_url",
                    description="Navigate to a URL with JavaScript disabled and capture HTML content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to navigate to"
                            },
                            "wait_time": {
                                "type": "number",
                                "description": "Time to wait after page load (seconds)",
                                "default": 3
                            }
                        },
                        "required": ["url"]
                    }
                ),
                types.Tool(
                    name="get_page_html",
                    description="Get the current page's HTML content",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_network_requests",
                    description="Get all captured network requests (XHR, API calls, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter_type": {
                                "type": "string",
                                "description": "Filter by request type (xhr, fetch, all)",
                                "default": "all"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="close_browser",
                    description="Close the browser and cleanup resources",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                if name == "navigate_to_url":
                    return await self._navigate_to_url(arguments)
                elif name == "get_page_html":
                    return await self._get_page_html()
                elif name == "get_network_requests":
                    return await self._get_network_requests(arguments)
                elif name == "close_browser":
                    return await self._close_browser()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _initialize_browser(self):
        """Initialize Camoufox browser with JavaScript enabled for network monitoring"""
        if self.camoufox is None:
            logger.info("Initializing Camoufox browser...")
            self.camoufox = AsyncCamoufox(
                headless=False
            )

            await self.camoufox.start()
            self.browser = self.camoufox.browser

            # Create a context with JavaScript enabled for network monitoring
            self.context = await self.browser.new_context(java_script_enabled=True)
            self.page = await self.context.new_page()

            # Setup network request monitoring
            await self._setup_network_monitoring()

            logger.info("Browser initialized successfully")

    async def _setup_network_monitoring(self):
        """Setup network request monitoring to capture XHR and API calls"""
        if not self.page:
            return

        # Clear previous requests
        self.network_requests = []

        # Monitor network requests
        async def handle_request(request):
            request_data = {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "resource_type": request.resource_type,
                "timestamp": asyncio.get_event_loop().time()
            }

            # Capture request body for POST requests
            if request.method.upper() in ["POST", "PUT", "PATCH"]:
                try:
                    request_data["body"] = request.post_data
                except:
                    request_data["body"] = None

            self.network_requests.append(request_data)
            logger.info(f"Captured request: {request.method} {request.url}")

        # Monitor responses
        async def handle_response(response):
            # Find the corresponding request
            for req in self.network_requests:
                if req["url"] == response.url and "response" not in req:
                    try:
                        # Capture response data for API calls
                        if response.headers.get("content-type", "").startswith(("application/json", "application/xml", "text/")):
                            content = await response.text()
                            req["response"] = {
                                "status": response.status,
                                "headers": dict(response.headers),
                                "content": content,
                                "content_type": response.headers.get("content-type", "")
                            }
                        else:
                            req["response"] = {
                                "status": response.status,
                                "headers": dict(response.headers),
                                "content_type": response.headers.get("content-type", ""),
                                "content": "[Binary or large content]"
                            }
                    except Exception as e:
                        req["response"] = {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "error": str(e)
                        }
                    break

        # Attach event listeners
        self.page.on("request", handle_request)
        self.page.on("response", handle_response)

    async def _navigate_to_url(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Navigate to a URL and return the HTML content"""
        url = arguments.get("url")
        wait_time = arguments.get("wait_time", 3)

        if not url:
            return [types.TextContent(type="text", text="Error: URL is required")]

        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return [types.TextContent(type="text", text="Error: Invalid URL format")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: Invalid URL - {str(e)}")]

        try:
            await self._initialize_browser()

            logger.info(f"Navigating to: {url}")

            # Clear previous network requests
            self.network_requests = []

            # Navigate to the URL
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for additional content to load
            await asyncio.sleep(wait_time)

            # Get page title and basic info
            title = await self.page.title()
            current_url = self.page.url

            result = {
                "success": True,
                "url": current_url,
                "title": title,
                "network_requests_captured": len(self.network_requests),
                "message": f"Successfully navigated to {url}. Captured {len(self.network_requests)} network requests."
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return [types.TextContent(type="text", text=f"Error navigating to URL: {str(e)}")]

    async def _get_page_html(self) -> List[types.TextContent]:
        """Get the current page's HTML content with JavaScript disabled"""
        if not self.page:
            return [types.TextContent(type="text", text="Error: No page loaded. Use navigate_to_url first.")]

        try:
            current_url = self.page.url

            # Create a new context with JavaScript disabled for clean HTML extraction
            js_disabled_context = await self.browser.new_context(java_script_enabled=False)
            js_disabled_page = await js_disabled_context.new_page()

            # Navigate to the same URL with JS disabled
            await js_disabled_page.goto(current_url, wait_until="domcontentloaded", timeout=30000)

            # Extract HTML content
            html_content = await js_disabled_page.content()

            # Clean up the temporary context
            await js_disabled_context.close()

            result = {
                "success": True,
                "url": current_url,
                "html_length": len(html_content),
                "html_content": html_content,
                "note": "HTML extracted with JavaScript disabled for clean content"
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Error getting page HTML: {e}")
            return [types.TextContent(type="text", text=f"Error getting page HTML: {str(e)}")]

    async def _get_network_requests(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get captured network requests"""
        filter_type = arguments.get("filter_type", "all").lower()

        try:
            filtered_requests = self.network_requests

            if filter_type == "xhr":
                filtered_requests = [req for req in self.network_requests if req.get("resource_type") == "xhr"]
            elif filter_type == "fetch":
                filtered_requests = [req for req in self.network_requests if req.get("resource_type") == "fetch"]

            result = {
                "success": True,
                "total_requests": len(self.network_requests),
                "filtered_requests": len(filtered_requests),
                "filter_applied": filter_type,
                "requests": filtered_requests
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Error getting network requests: {e}")
            return [types.TextContent(type="text", text=f"Error getting network requests: {str(e)}")]

    async def _close_browser(self) -> List[types.TextContent]:
        """Close the browser and cleanup resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

            self.camoufox = None
            self.browser = None
            self.context = None
            self.page = None
            self.network_requests = []

            logger.info("Browser closed successfully")
            return [types.TextContent(type="text", text="Browser closed successfully")]

        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            return [types.TextContent(type="text", text=f"Error closing browser: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    server_instance = CamoufoxMCPServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="camoufox-scraper",
                server_version="0.1.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
