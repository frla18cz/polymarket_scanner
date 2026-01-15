import unittest
from pydantic import ValidationError
from main import Holder, WalletStats, HolderDetail

class TestPydanticModels(unittest.TestCase):
    def test_holder_detail_has_alias(self):
        # Should be able to instantiate with alias
        h = HolderDetail(
            wallet_address="0x123",
            position_size=100.0,
            outcome_index=0,
            total_pnl=50.0,
            alias="Whale1"
        )
        self.assertEqual(h.alias, "Whale1")
        
        # Should be optional
        h2 = HolderDetail(
            wallet_address="0x123",
            position_size=100.0,
            outcome_index=0
        )
        self.assertIsNone(h2.alias)

    def test_wallet_stats_has_alias(self):
        # Should be able to instantiate with alias
        w = WalletStats(
            wallet_address="0x123",
            total_pnl=1000.0,
            last_updated="2024-01-01",
            alias="ProUser"
        )
        self.assertEqual(w.alias, "ProUser")

        # Should be optional
        w2 = WalletStats(
            wallet_address="0x123",
            total_pnl=1000.0,
            last_updated="2024-01-01"
        )
        self.assertIsNone(w2.alias)

if __name__ == '__main__':
    unittest.main()
