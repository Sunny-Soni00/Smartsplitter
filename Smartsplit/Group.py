from Debt import Debt

class Group:
    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.expenses = []
        self.debts = []

    def add_expense(self, expense):
        self.expenses.append(expense)
        self._update_debts(expense)

    def _update_debts(self, expense):
        payer = expense.payer
        for user, share in expense.splits.items():
            if user != payer:
                self._add_or_update_debt(user, payer, share)
        self._simplify_debts()

    def _add_or_update_debt(self, debtor, creditor, amount):
        for d in self.debts:
            if d.debtor == debtor and d.creditor == creditor:
                d.amount += amount
                return
            if d.debtor == creditor and d.creditor == debtor:
                if d.amount > amount:
                    d.amount -= amount
                elif d.amount < amount:
                    d.debtor, d.creditor = d.creditor, d.debtor
                    d.amount = amount - d.amount
                else:
                    self.debts.remove(d)
                return
        self.debts.append(Debt(debtor, creditor, amount))

    def _simplify_debts(self):
        changed = True
        while changed:
            changed = False
            for d1 in list(self.debts):
                for d2 in list(self.debts):
                    if d1 != d2 and d1.creditor == d2.debtor and d1.debtor != d2.creditor:
                        amount = min(d1.amount, d2.amount)
                        self._add_or_update_debt(d1.debtor, d2.creditor, amount)
                        d1.amount -= amount
                        d2.amount -= amount
                        changed = True
                        if d1.amount <= 0 and d1 in self.debts:
                            self.debts.remove(d1)
                        if d2.amount <= 0 and d2 in self.debts:
                            self.debts.remove(d2)
                        break
                if changed:
                    break

    def show_debts(self):
        if not self.debts:
            print("No debts in this group.")
            return
        for debt in self.debts:
            print(f"{debt.debtor.name} owes {debt.creditor.name} ₹{debt.amount:.2f}")

    def settle_up(self, payer_name, receiver_name, amount):
        payer = next((u for u in self.members if u.name == payer_name), None)
        receiver = next((u for u in self.members if u.name == receiver_name), None)
        if not payer or not receiver:
            print("Invalid user.")
            return
        for d in self.debts:
            if d.debtor == payer and d.creditor == receiver:
                if amount >= d.amount:
                    self.debts.remove(d)
                else:
                    d.amount -= amount
                break
        else:
            print("No debt found between users.")
        self._simplify_debts()