import unittest

from services.finance_service import calculate_profit, get_cashflow_summary, get_monthly_cashflow


class FinanceServiceTest(unittest.TestCase):
    def test_cashflow_summary(self):
        summary = get_cashflow_summary()
        self.assertIn("income", summary)
        self.assertIn("expense", summary)

    def test_monthly_cashflow(self):
        cashflow = get_monthly_cashflow()
        self.assertFalse(cashflow.empty)
        self.assertIn("净现金流", cashflow.columns)

    def test_profit_number(self):
        self.assertIsInstance(calculate_profit(), float)


if __name__ == "__main__":
    unittest.main()

