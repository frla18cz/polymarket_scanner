import asyncio
import os
import time
import subprocess
import signal
from playwright.async_api import async_playwright

# Injected script for visual cursor and click effects
MOUSE_HELPER_JS = """
(() => {
  const box = document.createElement('div');
  box.classList.add('mouse-helper');
  const style = document.createElement('style');
  style.innerHTML = `
    .mouse-helper {
      pointer-events: none;
      position: absolute;
      top: 0;
      left: 0;
      width: 20px;
      height: 20px;
      background: rgba(46, 117, 255, 0.8);
      border: 2px solid white;
      border-radius: 50%;
      z-index: 10000;
      transform: translate(-50%, -50%);
      transition: all 0.1s ease-out;
      box-shadow: 0 0 10px rgba(46, 117, 255, 0.5);
    }
    .mouse-helper.clicking {
      transform: translate(-50%, -50%) scale(0.8);
      background: rgba(0, 195, 136, 0.9);
    }
    .click-ripple {
      position: absolute;
      border-radius: 50%;
      border: 2px solid rgba(46, 117, 255, 0.6);
      transform: translate(-50%, -50%);
      animation: ripple 0.6s linear;
      pointer-events: none;
      z-index: 9999;
    }
    @keyframes ripple {
      0% { width: 0; height: 0; opacity: 1; }
      100% { width: 50px; height: 50px; opacity: 0; }
    }
  `;
  document.head.appendChild(style);
  document.body.appendChild(box);

  window.updateMouseHelper = (x, y) => {
    box.style.left = x + 'px';
    box.style.top = y + 'px';
  };

  window.clickMouseHelper = () => {
    box.classList.add('clicking');
    const ripple = document.createElement('div');
    ripple.classList.add('click-ripple');
    ripple.style.left = box.style.left;
    ripple.style.top = box.style.top;
    document.body.appendChild(ripple);
    setTimeout(() => {
      box.classList.remove('clicking');
      ripple.remove();
    }, 200);
  };
})();
"""

async def generate_demo():
    print("Starting FastAPI server...")
    env = os.environ.copy()
    env["SERVE_FRONTEND"] = "1"
    
    out_log = open("server_out.log", "w")
    err_log = open("server_err.log", "w")
    
    server_process = subprocess.Popen(
        ["python", "main.py"],
        stdout=out_log,
        stderr=err_log,
        env=env
    )
    
    time.sleep(5) # Warmup
    
    try:
        async with async_playwright() as p:
            # Launch with video recording enabled
            browser = await p.chromium.launch(headless=True) # Headless works for video too
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}, # 720p HD
                record_video_dir="static/assets/",
                record_video_size={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            # Navigate
            try:
                await page.goto("http://127.0.0.1:8000", timeout=10000)
            except Exception as e:
                print(f"Failed to navigate: {e}")
                raise

            # Inject visual helper
            await page.evaluate(MOUSE_HELPER_JS)

            # Custom interaction helper to animate mouse
            async def smooth_move(selector=None, x=None, y=None, steps=10):
                if selector:
                    box = await selector.bounding_box()
                    if not box: return
                    target_x = box['x'] + box['width'] / 2
                    target_y = box['y'] + box['height'] / 2
                else:
                    target_x, target_y = x, y

                # We don't know current pos easily in headless without tracking, 
                # so we just teleport/move quickly for now or assume last pos.
                # Playwright's mouse.move is instant, so we fake steps.
                # For simplicity in this script, we just move directly but update the visual helper.
                
                await page.mouse.move(target_x, target_y, steps=steps)
                await page.evaluate(f"window.updateMouseHelper({target_x}, {target_y})")
                await asyncio.sleep(0.1)

            async def click_element(selector):
                await smooth_move(selector, steps=15)
                await page.evaluate("window.clickMouseHelper()")
                await selector.click()
                await asyncio.sleep(0.5) # Pause after click

            print("Scenario: Start...")
            await asyncio.sleep(2)

            # 2. Include Categories -> ALL
            print("Scenario: Reset Categories...")
            # Using text locators is risky if text changes, but good for demo readability
            all_btn = page.get_by_role("button", name="ALL")
            await click_element(all_btn)

            # 3. Expiration -> 30d
            print("Scenario: Set Expiration...")
            # Find the '30d' button under Expires Within
            # The UI has multiple '30d' buttons (expiry vs min expiry), we need to be specific.
            # L1234: <button ... @click="applyExpiryPreset('30d')">
            # We can use the text "30d" and ensure it's the one in the first block (Expires Within)
            # A robust way is to click the specific button.
            # Let's find the container first.
            btns_30d = page.get_by_role("button", name="30d")
            # Usually the first one is "Expires Within" based on layout
            await click_element(btns_30d.first)

            # 4. Price Range 90-99%
            print("Scenario: Set Price Range...")
            # Sliders are tricky to drag in Playwright. We can interact with the inputs directly if they were inputs,
            # but here they are range inputs. We can set their value via JS or keyboard.
            # Focus Min Price slider (index 1 in the inputs list usually? Let's check visually or use IDs if we had them)
            # Based on HTML structure:
            # 1. Expiry Index
            # 2. Min Price
            # 3. Max Price
            # 4. Max Spread
            # 5. Min APR
            # 6. Min Volume
            # 7. Min Liquidity
            
            sliders = page.locator('input[type="range"]')
            
            # Min Price (Slider 1) -> 90% (0.90)
            min_price_slider = sliders.nth(1)
            # We can force the value via JS for precision in the demo
            await min_price_slider.evaluate("el => { el.value = 90; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            # Move mouse there to "show" we did it
            await smooth_move(min_price_slider)
            await asyncio.sleep(0.5)

            # Max Price (Slider 2) -> 99% (0.99)
            max_price_slider = sliders.nth(2)
            await max_price_slider.evaluate("el => { el.value = 99; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await smooth_move(max_price_slider)
            await asyncio.sleep(0.5)

            # 5. Constraints
            print("Scenario: Set Constraints...")
            
            # Max Spread (Slider 3) -> 0.02 (2 cents)
            spread_slider = sliders.nth(3)
            await spread_slider.evaluate("el => { el.value = 0.02; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await smooth_move(spread_slider)
            await asyncio.sleep(0.5)

            # Min Volume (Slider 5) -> 10,000
            # Note: Slider 4 is APR.
            vol_slider = sliders.nth(5)
            await vol_slider.evaluate("el => { el.value = 10000; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await smooth_move(vol_slider)
            await asyncio.sleep(0.5)
            
            # Min Liquidity (Slider 6) -> 3,000
            liq_slider = sliders.nth(6)
            await liq_slider.evaluate("el => { el.value = 3000; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await smooth_move(liq_slider)
            await asyncio.sleep(1.0)

            # 6. Results
            print("Scenario: Show Results...")
            # Scroll down to table
            await page.evaluate("window.scrollTo({top: 500, behavior: 'smooth'})")
            await asyncio.sleep(1)
            
            # Hover over the first result row to highlight it
            # Using class .group or just the first row ID
            first_row = page.locator("#row-0")
            if await first_row.count() > 0:
                await smooth_move(first_row)
                await first_row.hover()
                await asyncio.sleep(2)
            else:
                print("No results found to hover!")

            await asyncio.sleep(2) # Hold final frame
            
            await context.close() # Saves the video
            await browser.close()
            
            # Rename the video file (Playwright saves with a random name)
            # Find the latest .webm in static/assets/
            files = os.listdir("static/assets/")
            webm_files = [f for f in files if f.endswith(".webm")]
            if webm_files:
                # Get the most recent one
                latest_video = max([os.path.join("static/assets/", f) for f in webm_files], key=os.path.getctime)
                webm_path = "static/assets/demo.webm"
                
                # Remove old if exists
                if os.path.exists(webm_path):
                    os.remove(webm_path)
                    
                os.rename(latest_video, webm_path)
                print(f"Raw video saved to {webm_path}")
                
                # Convert to MP4 and GIF
                print("Converting to MP4 and GIF...")
                try:
                    from moviepy import VideoFileClip
                    
                    clip = VideoFileClip(webm_path)
                    
                    # MP4
                    mp4_path = "static/assets/demo.mp4"
                    clip.write_videofile(mp4_path, codec="libx264", audio=False)
                    print(f"Saved {mp4_path}")
                    
                    # GIF
                    gif_path = "static/assets/demo.gif"
                    clip.write_gif(gif_path, fps=10)
                    print(f"Saved {gif_path}")
                    
                    clip.close()
                except Exception as e:
                    print(f"Conversion failed: {e}")
                
    finally:
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        out_log.close()
        err_log.close()

if __name__ == "__main__":
    asyncio.run(generate_demo())