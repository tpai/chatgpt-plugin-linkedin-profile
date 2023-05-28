from fastapi import FastAPI
from routers.wellknown import wellknown
from fastapi.middleware.cors import CORSMiddleware
from pyppeteer import launch, connect
from scrape_profile import get_profile_from_html
import asyncio
import socket
import json
import os

app = FastAPI()
app.include_router(wellknown)
app.add_middleware(CORSMiddleware, allow_origins=["https://chat.openai.com"])

# Retrieve IP address from CHROME_HOST using DNS query
CHROME_HOST = os.environ.get("CHROME_HOST", "localhost")
chrome_ip = socket.gethostbyname(CHROME_HOST)
chrome_port = os.environ.get("CHROME_PORT", "9222")
print(chrome_ip, chrome_port)

@app.get("/profile", summary="Get user profile", operation_id="getProfile")
async def get_profile(query: str = None):

    # wait until chrome is alive
    async def wait_for_chrome():
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                with socket.create_connection((chrome_ip, chrome_port), timeout=1):
                    print('Checking health for chrome...')
                    break
            except OSError:
                await asyncio.sleep(1)
                if asyncio.get_event_loop().time() - start_time > 30:
                    raise TimeoutError("Connection to chrome timed out after 30 seconds")
    try:
        await wait_for_chrome()
    except Exception as e:
        print(f"Error occurred: {e}")
        output = {"error": "An error occurred while connecting to the instance."}
        return output

    # Connect to the remote browser using the IP address
    browser = await connect(browserURL=f"http://{chrome_ip}:{chrome_port}")
    context = await browser.createIncognitoBrowserContext()
    print("Chrome is healthy")

    # Create a new page
    page = await context.newPage()

    try:
        if query:
            # Retrieve username from query
            username = query.lower().strip()
            # Construct the LinkedIn URL
            url = f"https://linkedin.com/in/{username}/"
        else:
            # Default LinkedIn URL
            url = "https://linkedin.com/in/ryanroslansky/"

        # Set the user-agent header
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
        # Navigate to the specified URL
        await page.goto(url)

        await page.waitFor("main[id='main-content']")
        await page.waitFor("section[class*='summary']")
        page_html = await page.evaluate("""() => document.body.outerHTML""")
        output = get_profile_from_html(page_html)
    except Exception as e:
        print(f"Error occurred: {e}")
        output = {"error": "An error occurred while processing the request."}
    finally:
        await page.close()
    return output

