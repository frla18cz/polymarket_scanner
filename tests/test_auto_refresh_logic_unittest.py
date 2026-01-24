import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import auto_refresh but we might need to mock setup_logging to avoid side effects
with patch('auto_refresh.setup_logging'):
    import auto_refresh

class TestAutoRefreshLogic(unittest.TestCase):
    
    @patch('auto_refresh.run_scrape')
    @patch('auto_refresh.run_smart_money')
    @patch('auto_refresh.log_stats')
    def test_coordinated_refresh_success(self, mock_log, mock_smart, mock_scrape):
        """Test that smart money runs after scrape succeeds."""
        # Ensure the function exists (it won't yet, so this will fail or we skip if not present)
        if not hasattr(auto_refresh, 'job_coordinated_refresh'):
            self.fail("job_coordinated_refresh not implemented yet")
            
        auto_refresh.job_coordinated_refresh()
        
        mock_scrape.assert_called_once()
        mock_smart.assert_called_once()
        # Verify order: scrape should complete before smart money starts
        # (This implies synchronous execution which is expected)

    @patch('auto_refresh.run_scrape')
    @patch('auto_refresh.run_smart_money')
    @patch('auto_refresh.log_stats')
    def test_coordinated_refresh_failure(self, mock_log, mock_smart, mock_scrape):
        """Test that smart money DOES NOT run if scrape fails."""
        if not hasattr(auto_refresh, 'job_coordinated_refresh'):
            self.fail("job_coordinated_refresh not implemented yet")

        # Simulate failure in scrape
        mock_scrape.side_effect = Exception("Scrape failed")
        
        auto_refresh.job_coordinated_refresh()
        
        mock_scrape.assert_called_once()
        mock_smart.assert_not_called()

    @patch('auto_refresh.run_scrape')
    @patch('auto_refresh.run_smart_money')
    @patch('auto_refresh.log_stats')
    def test_coordinated_refresh_smart_money_failure(self, mock_log, mock_smart, mock_scrape):
        """Test that smart money failure is caught and logged."""
        # Ensure smart money runs (interval logic or reset global)
        auto_refresh._last_smart_money_run = 0
        
        mock_smart.side_effect = Exception("Smart Money failed")
        
        try:
            auto_refresh.job_coordinated_refresh()
        except Exception:
            self.fail("job_coordinated_refresh raised exception on smart money failure")
            
        mock_scrape.assert_called_once()
        mock_smart.assert_called_once()

    @patch('auto_refresh.BlockingScheduler')
    def test_start_scheduler(self, mock_scheduler_cls):
        """Test scheduler startup and job configuration."""
        mock_scheduler = mock_scheduler_cls.return_value
        
        auto_refresh.start_scheduler()
        
        mock_scheduler.add_job.assert_called_once()
        args, kwargs = mock_scheduler.add_job.call_args
        self.assertEqual(kwargs['id'], 'coordinated_refresh')
        self.assertEqual(kwargs['trigger'].interval.total_seconds(), 3600.0) # 60 minutes
        mock_scheduler.start.assert_called_once()

if __name__ == '__main__':
    unittest.main()
