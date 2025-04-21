from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from .models import MonthlyFinanceSummary

class MonthlyFinanceSummaryTestCase(TestCase):
    def setUp(self):
        # Create a dummy user (shop owner)
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a MonthlyFinanceSummary instance
        self.summary = MonthlyFinanceSummary.objects.create(
            shop=self.user,
            month=4,
            year=2025,
            total_sales=Decimal('70000.00'),
            total_income=Decimal('60000.00'),
            total_expenses=Decimal('30000.00'),
        )

    def test_calculate_profit(self):
        # Run the profit calculation method
        self.summary.calculate_profit()

        # Refresh from DB
        self.summary.refresh_from_db()

        # Check if profit is correct
        self.assertEqual(self.summary.profit, Decimal('30000.00'))

        # Check if profit margin is correct: (30000 / 60000) * 100 = 50
        self.assertEqual(self.summary.profit_margin, Decimal('50.00'))
