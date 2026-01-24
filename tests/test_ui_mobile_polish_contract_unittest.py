import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"

class TestUiMobilePolishContract(unittest.TestCase):
    def test_mobile_filters_do_not_auto_open(self):
        """
        Ensures that the 'filters-first' logic (auto-opening filters on mobile if not seen)
        is REMOVED to satisfy the 'results-first' requirement.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # We expect showMobileFilters to be initialized to false
        # (This is likely already true, but let's verify no one set it to true by default)
        self.assertRegex(html, r"const\s+showMobileFilters\s*=\s*ref\s*\(\s*false\s*\)", 
                         "showMobileFilters should be initialized to false")

        # The function `maybeAutoOpenMobileFilters` logic that sets it to true
        # should either be removed or significantly altered.
        # For this test, we assert that the specific auto-open logic is GONE.
        
        # The specific line we want to disappear: `showMobileFilters.value = true;` inside `maybeAutoOpenMobileFilters`
        # We can look for the function definition and check its content, or just check that the function call in onMounted is gone/changed.
        
        # Let's search for the aggressive auto-open pattern
        auto_open_pattern = r"showMobileFilters\.value\s*=\s*true;\s*_safeSetLocalStorage\(MOBILE_FILTERS_SEEN_KEY,\s*\"1\"\);"
        
        self.assertNotRegex(html, auto_open_pattern, 
                            "The code should NOT auto-open mobile filters on first visit. Found legacy auto-open logic.")

    def test_market_fetching_logic_is_independent_of_filters_visibility(self):
        """
        Ensures that data fetching happens regardless of filter visibility.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # Ensure 'debouncedFetch' or 'resetAndFetch' is called on mount
        # or that 'onMounted' calls something that fetches data.
        
        # We assume onMounted calls `resetAndFetch` or `loadMore` or similar.
        # Let's verify onMounted exists and calls a fetcher.
        
        match = re.search(r"onMounted\(\s*(?:async\s+)?\(\)\s*=>\s*\{([\s\S]*?)\}\);", html)
        self.assertIsNotNone(match, "onMounted hook not found")
        
        on_mounted_body = match.group(1)
        
        # It should call fetch/load
        self.assertTrue("resetAndFetch" in on_mounted_body or "loadMore" in on_mounted_body or "debouncedFetch" in on_mounted_body or "fetchMarkets" in on_mounted_body, 
                        "onMounted must initiate data fetching")
        
        # It should NOT condition the fetch on showMobileFilters
        self.assertNotIn("if (showMobileFilters.value)", on_mounted_body, 
                         "Fetching should not be conditional on filter visibility")

    def test_mobile_filter_modal_structure(self):
        """
        Verifies the structure of the new bottom-sheet filter modal.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # Pull handle
        self.assertIn('w-12 h-1.5 bg-gray-700 rounded-full mx-auto my-3', html, 
                      "Mobile pull handle missing from filter modal")
        
        # Show Results sticky button
        self.assertIn('Show Results', html, "Sticky 'Show Results' button missing")
        self.assertIn('markets.length', html, "Results counter missing from sticky button")
        
        # Advanced section toggle
        self.assertIn('showAdvancedFilters = !showAdvancedFilters', html, 
                      "Advanced filters toggle logic missing")
        self.assertIn('v-show="!isNarrowScreen || showAdvancedFilters"', html, 
                      "Advanced filters visibility logic missing")

    def test_show_advanced_filters_state_exists(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        self.assertRegex(html, r"const\s+showAdvancedFilters\s*=\s*ref\s*\(\s*false\s*\)", 
                         "showAdvancedFilters should be initialized to false")

    def test_active_filter_chips_ui_exists(self):
        """
        Verifies that active filter chips are rendered above the market list.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # Check for the chips container
        self.assertIn('activeFilterChips', html, "activeFilterChips v-for loop missing")
        self.assertIn('removeFilterChip(chip.key)', html, "removeFilterChip click binding missing")
        self.assertIn('Clear All', html, "Clear All button for chips missing")

    def test_remove_filter_chip_method_exists(self):
        """
        Verifies that the removeFilterChip method is implemented in the script.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        self.assertIn('const removeFilterChip = (key) =>', html, "removeFilterChip method missing from script")
        self.assertIn('resetAndFetch()', html, "removeFilterChip should trigger re-fetch")

    def test_mobile_filter_hint_exists(self):
        """
        Verifies that the first-visit hint tooltip is implemented.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        self.assertRegex(html, r"const\s+showMobileFilterHint\s*=\s*ref\s*\(\s*false\s*\)", 
                         "showMobileFilterHint state missing")
        self.assertIn('Tip: Tap here to adjust filters!', html, "Hint tooltip text missing")
        self.assertIn('dismissMobileFilterHint()', html, "dismissMobileFilterHint call missing")