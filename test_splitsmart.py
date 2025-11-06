import unittest
from Smartsplit import User, Expense, Group


class TestSplitSmart(unittest.TestCase):

    # 1️⃣ TESTING EXPENSE SPLITTING
    def test_equal_split(self):
        u1 = User("Alice", "a@example.com")
        u2 = User("Bob", "b@example.com")
        exp = Expense("Lunch", 100, u1, [u1, u2], "equal")
        self.assertEqual(exp.splits[u1], 50.0)
        self.assertEqual(exp.splits[u2], 50.0)

    def test_unequal_split(self):
        u1 = User("Alice", "a@example.com")
        u2 = User("Bob", "b@example.com")
        shares = {u1: 70, u2: 30}
        exp = Expense("Taxi", 100, u1, [u1, u2], "unequal", shares)
        self.assertAlmostEqual(exp.splits[u1], 70.0)
        self.assertAlmostEqual(exp.splits[u2], 30.0)

    def test_percent_split(self):
        u1 = User("Alice", "a@example.com")
        u2 = User("Bob", "b@example.com")
        shares = {u1: 60, u2: 40}
        exp = Expense("Dinner", 200, u1, [u1, u2], "percent", shares)
        self.assertEqual(exp.splits[u1], 120.0)
        self.assertEqual(exp.splits[u2], 80.0)


    # 2️⃣ TESTING EXPENSE ADDITION AND DEBT CREATION
    def test_add_expense_creates_debt(self):
        u1 = User("Alice", "a@example.com")
        u2 = User("Bob", "b@example.com")
        g = Group("Trip", [u1, u2])
        exp = Expense("Lunch", 100, u1, [u1, u2], "equal")
        g.add_expense(exp)

        # Check that one debt is created
        self.assertEqual(len(g.debts), 1)
        d = g.debts[0]
        self.assertEqual(d.debtor, u2)
        self.assertEqual(d.creditor, u1)
        self.assertEqual(d.amount, 50.0)


    # 3️⃣ TESTING DEBT UPDATES AND SETTLEMENT
    def test_settle_up_clears_debt(self):
        u1 = User("Alice", "a@example.com")
        u2 = User("Bob", "b@example.com")
        g = Group("Trip", [u1, u2])
        exp = Expense("Dinner", 100, u1, [u1, u2], "equal")
        g.add_expense(exp)

        # Bob pays Alice back 50 → should clear debt
        g.settle_up("Bob", "Alice", 50.0)
        self.assertEqual(len(g.debts), 0)


if __name__ == "__main__":
    unittest.main()
