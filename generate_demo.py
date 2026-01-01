import asyncio
import os
import time
from playwright.async_api import async_playwright
from PIL import Image
import subprocess
import signal

async def generate_demo():
    # 1. Start the server
    print("Starting FastAPI server...")
    env = os.environ.copy()
    env["SERVE_FRONTEND"] = "1"
    
    # Log server output to files for debugging
    out_log = open("server_out.log", "w")
    err_log = open("server_err.log", "w")
    
    server_process = subprocess.Popen(
        ["python", "main.py"],
        stdout=out_log,
        stderr=err_log,
        env=env
    )
    
    # Wait for server to be ready
    time.sleep(5)
    
    frames = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Use a consistent viewport for high quality
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            print("Navigating to PolyLab...")
            try:
                await page.goto("http://127.0.0.1:8000", timeout=10000)
            except Exception as e:
                print(f"Failed to navigate: {e}")
                # Check server logs
                with open("server_err.log", "r") as f:
                    print("Server Errors:")
                    print(f.read())
                raise
            
            # Helper to capture frames
            async def capture(duration_sec, fps=10):
                for _ in range(int(duration_sec * fps)):
                    screenshot_bytes = await page.screenshot()
                    from io import BytesIO
                    img = Image.open(BytesIO(screenshot_bytes))
                    frames.append(img)
                    await asyncio.sleep(1/fps)

            print("Capturing initial state...")
            await capture(2) # Initial view
            
            print("Interacting: Filtering Volume...")
            # Adjust Volume slider (approximate)
            slider = page.locator('input[type="range"]').nth(3) 
            await slider.focus()
            for _ in range(5): # Fewer steps for speed
                await page.keyboard.press("ArrowRight")
                await capture(0.2)

            print("Interacting: Sorting by Spread...")
            await page.get_by_text("Spread", exact=True).click()
            await capture(2)
            
            print("Interacting: Searching for 'Election'...")
            search_input = page.locator('input[placeholder*="Trump, BTC, etc..."]')
            await search_input.click()
            for char in "Election":
                await page.keyboard.type(char)
                await capture(0.1)
            
            await capture(2) # Final view
            
            await browser.close()
    finally:
        # Stop the server
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        out_log.close()
        err_log.close()
    
    # Save as GIF
    if frames:
        print(f"Saving {len(frames)} frames to static/assets/demo.gif...")
        output_path = "static/assets/demo.gif"
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=100, # 100ms per frame = 10fps
            loop=0
        )
        print("Demo GIF generated successfully!")
    else:
        print("No frames captured!")

if __name__ == "__main__":
    asyncio.run(generate_demo())
