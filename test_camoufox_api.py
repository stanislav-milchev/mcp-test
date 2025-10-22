#!/usr/bin/env python3
"""
Test script to validate Camoufox API usage for the MCP server.
"""

import asyncio
import logging
from camoufox import AsyncCamoufox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_camoufox_workflow():
    """Test the complete Camoufox workflow that our MCP server will use"""
    
    camoufox = None
    browser = None
    page = None
    
    try:
        # 1. Initialize Camoufox
        logger.info("1. Initializing Camoufox...")
        camoufox = AsyncCamoufox(
            headless=True
        )
        
        # 2. Start browser
        logger.info("2. Starting browser...")
        await camoufox.start()
        browser = camoufox.browser
        
        # 3. Create new page
        logger.info("3. Creating new page...")
        page = await browser.new_page()
        
        # 4. Setup network monitoring
        logger.info("4. Setting up network monitoring...")
        network_requests = []
        
        async def handle_request(request):
            request_data = {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "resource_type": request.resource_type,
            }
            network_requests.append(request_data)
            logger.info(f"Captured request: {request.method} {request.url}")
        
        async def handle_response(response):
            logger.info(f"Response: {response.status} {response.url}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # 5. Navigate to a test URL
        logger.info("5. Navigating to example.com...")
        await page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
        
        # 6. Wait and get page info
        await asyncio.sleep(2)
        title = await page.title()
        current_url = page.url
        html_content = await page.content()
        
        # 7. Display results
        logger.info(f"✓ Page loaded successfully")
        logger.info(f"  Title: {title}")
        logger.info(f"  URL: {current_url}")
        logger.info(f"  HTML length: {len(html_content)}")
        logger.info(f"  Network requests captured: {len(network_requests)}")
        
        for i, req in enumerate(network_requests[:5]):  # Show first 5
            logger.info(f"  Request {i+1}: {req['method']} {req['url']} ({req['resource_type']})")
            
        # 8. Close browser
        logger.info("8. Closing browser...")
        await browser.close()
        
        logger.info("✓ Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            if browser:
                await browser.close()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(test_camoufox_workflow())
    if success:
        print("\n✓ All API calls work correctly! The MCP server implementation should work.")
    else:
        print("\n✗ API test failed. Need to fix the implementation.")