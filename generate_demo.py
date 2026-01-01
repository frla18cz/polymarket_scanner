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
      width: 24px;
      height: 24px;
      background: rgba(46, 117, 255, 0.9);
      border: 3px solid white;
      border-radius: 50%;
      z-index: 10000;
      transform: translate(-50%, -50%);
      transition: width 0.2s, height 0.2s, background 0.2s;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .mouse-helper.clicking {
      width: 20px;
      height: 20px;
      background: rgba(0, 195, 136, 1);
    }
    .click-ripple {
      position: absolute;
      border-radius: 50%;
      border: 3px solid rgba(46, 117, 255, 0.8);
      transform: translate(-50%, -50%);
      animation: ripple 0.8s ease-out;
      pointer-events: none;
      z-index: 9999;
    }
    @keyframes ripple {
      0% { width: 0; height: 0; opacity: 1; border-width: 3px; }
      100% { width: 80px; height: 80px; opacity: 0; border-width: 0px; }
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
    }, 250);
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
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}, # Full HD
                device_scale_factor=2, # Retina quality for sharper text
                record_video_dir="static/assets/",
                record_video_size={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Navigate
            try:
                await page.goto("http://127.0.0.1:8000", timeout=15000)
            except Exception as e:
                print(f"Failed to navigate: {e}")
                raise

            # Inject visual helper
            await page.evaluate(MOUSE_HELPER_JS)

            # Custom interaction helper to animate mouse
            async def smooth_move(selector=None, x=None, y=None, steps=40):
                if selector:
                    box = await selector.bounding_box()
                    if not box: return
                    target_x = box['x'] + box['width'] / 2
                    target_y = box['y'] + box['height'] / 2
                else:
                    target_x, target_y = x, y

                await page.mouse.move(target_x, target_y, steps=steps)
                await page.evaluate(f"window.updateMouseHelper({target_x}, {target_y})")
                await asyncio.sleep(0.2)

            async def click_element(selector):
                await smooth_move(selector, steps=50) # Slower approach
                await asyncio.sleep(0.3) # Hover verification pause
                await page.evaluate("window.clickMouseHelper()")
                await selector.click()
                await asyncio.sleep(1.0) # Longer pause after click

            print("Scenario: Start (3s pause)...")
            await asyncio.sleep(3)

            # 2. Include Categories -> ALL
            print("Scenario: Reset Categories...")
            all_btn = page.get_by_role("button", name="ALL")
            await click_element(all_btn)

            # 3. Expiration -> 30d
            print("Scenario: Set Expiration...")
            # "30d" is unique to the Expires Within preset list (Not Sooner Than uses 24h, 48h, 7d)
            btn_30d = page.locator("button", has_text="30d")
            await click_element(btn_30d)

            # 4. Price Range 90-99%
            print("Scenario: Set Price Range...")
            sliders = page.locator('input[type="range"]')
            
            # Min Price (Slider 1) -> 90% (0.90)
            min_price_slider = sliders.nth(1)
            await smooth_move(min_price_slider)
            await min_price_slider.evaluate("el => { el.value = 90; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await asyncio.sleep(1.0)

            # Max Price (Slider 2) -> 99% (0.99)
            max_price_slider = sliders.nth(2)
            await smooth_move(max_price_slider)
            await max_price_slider.evaluate("el => { el.value = 99; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await asyncio.sleep(1.0)

            # 5. Constraints
            print("Scenario: Set Constraints...")
            
            # Max Spread (Slider 3) -> 0.02 (2 cents)
            spread_slider = sliders.nth(3)
            await smooth_move(spread_slider)
            await spread_slider.evaluate("el => { el.value = 0.02; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await asyncio.sleep(1.0)

            # Min Volume (Slider 5) -> 10,000
            vol_slider = sliders.nth(5)
            await smooth_move(vol_slider)
            await vol_slider.evaluate("el => { el.value = 10000; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await asyncio.sleep(1.0)
            
            # Min Liquidity (Slider 6) -> 3,000
            liq_slider = sliders.nth(6)
            await smooth_move(liq_slider)
            await liq_slider.evaluate("el => { el.value = 3000; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }")
            await asyncio.sleep(1.5)

            # 6. Results
            print("Scenario: Show Results...")
            # Scroll down to table slowly
            await page.evaluate("window.scrollTo({top: 500, behavior: 'smooth'})")
            await asyncio.sleep(2)
            
            # Move mouse over rows to show interactivity
            first_row = page.locator("#row-0")
            second_row = page.locator("#row-1")
            
            if await first_row.count() > 0:
                await smooth_move(first_row, steps=60)
                await first_row.hover()
                await asyncio.sleep(1.5)
            
            if await second_row.count() > 0:
                await smooth_move(second_row, steps=40)
                await second_row.hover()
                await asyncio.sleep(1.5)

            await asyncio.sleep(3) # Hold final frame
            
            await context.close() # Saves the video
            await browser.close()
            
            # Rename/Convert
            files = os.listdir("static/assets/")
            webm_files = [f for f in files if f.endswith(".webm")]
            if webm_files:
                latest_video = max([os.path.join("static/assets/", f) for f in webm_files], key=os.path.getctime)
                webm_path = "static/assets/demo.webm"
                
                if os.path.exists(webm_path): os.remove(webm_path)
                os.rename(latest_video, webm_path)
                print(f"Raw video saved to {webm_path}")
                
                print("Converting to High Quality MP4...")
                try:
                    from moviepy import VideoFileClip
                    
                    clip = VideoFileClip(webm_path)
                    
                    # MP4 High Quality
                    mp4_path = "static/assets/demo.mp4"
                    clip.write_videofile(
                        mp4_path, 
                        codec="libx264", 
                        audio=False,
                        bitrate="5000k", # High bitrate for 1080p
                        preset="slow"    # Better compression quality
                    )
                    print(f"Saved {mp4_path}")
                    
                    # GIF (1080p GIF is insane, resizing to 800px width for email compatibility)
                    print("Generating Optimized GIF...")
                    gif_path = "static/assets/demo.gif"
                    
                    # Resize for GIF to keep it manageable (but still high quality)
                    # 1920 is too big for email. 1000px is a good compromise.
                    clip_resized = clip.resized(width=1000) 
                    clip_resized.write_gif(gif_path, fps=10)
                    print(f"Saved {gif_path}")
                    
                    clip.close()
                except Exception as e:
                    print(f"Conversion failed: {e}")
                    import traceback
                    traceback.print_exc()
                
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
