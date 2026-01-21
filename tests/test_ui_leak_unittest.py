import unittest
import subprocess
import os
import time
import asyncio
import signal
from playwright.async_api import async_playwright

class TestUILeak(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server
        cls.env = os.environ.copy()
        cls.env["SERVE_FRONTEND"] = "1"
        cls.server_process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=cls.env
        )
        # Give it time to start
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        if cls.server_process:
            cls.server_process.terminate()
            try:
                cls.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.server_process.kill()

    async def test_infinite_append_leak(self):
        """
        Verify that auto-refresh does not infinitely append items to the DOM.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 1. Load the page
            try:
                await page.goto("http://127.0.0.1:8000", timeout=10000)
            except Exception as e:
                self.fail(f"Failed to load page: {e}")

            # Wait for initial load (look for at least one item)
            # The v-for div has class "border-b" and "border-poly-accent/50"
            # Better selector: we can check the length of markets.value in JS, 
            # or count elements. Let's count elements to be sure about DOM.
            item_selector = "div.border-b.border-poly-accent\/50"
            
            # Wait for items to appear
            await page.wait_for_selector(item_selector, timeout=10000)
            
            # Initial count
            initial_count = await page.locator(item_selector).count()
            print(f"Initial count: {initial_count}")
            
            # We expect ~100 items (default limit)
            self.assertGreater(initial_count, 0, "No markets loaded initially")
            
            # 2. Fast-forward time to trigger intervals
            # We can't easily fast-forward setInterval in the browser from outside 
            # without mocking the clock. Waiting is more reliable for a reproduction script.
            # We will wait for slightly more than 30s to trigger the first refresh.
            print("Waiting 35s for first auto-refresh...")
            await asyncio.sleep(35)
            
            count_after_first = await page.locator(item_selector).count()
            print(f"Count after 35s: {count_after_first}")
            
            # 3. Wait again
            print("Waiting 35s for second auto-refresh...")
            await asyncio.sleep(35)
            
            count_after_second = await page.locator(item_selector).count()
            print(f"Count after 70s: {count_after_second}")
            
            # FAILURE CONDITION: usage grows. 
            # If bug exists: initial (~100) -> first (~200) -> second (~300)
            
            # To pass (fix), counts should be equal (or very close if live data changes slightly)
            # But definitely not doubling.
            
            # For this "Red" phase, we expect this assertion to FAIL if the bug exists.
            # So to confirm the bug, we can assert that it DOES grow, 
            # but standard TDD writes the test asserting correct behavior (which fails now).
            
            self.assertEqual(
                count_after_second, 
                initial_count, 
                f"Memory Leak Detected! Item count grew from {initial_count} to {count_after_second}"
            )

            await browser.close()
