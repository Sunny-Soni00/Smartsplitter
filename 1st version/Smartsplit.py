
import json
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class Expense:
    def __init__(self, description, amount, payer, participants, split_type, shares=None):
        self.description = description
        self.amount = amount
        self.payer = payer
        self.participants = participants
        self.split_type = split_type
        self.shares = shares or {}
        self.splits = self.calculate_shares()

    def calculate_shares(self):
        n = len(self.participants)
        splits = {}
        if self.split_type == 'equal':
            share = round(self.amount / n, 2)
            for p in self.participants:
                splits[p] = share
        elif self.split_type == 'unequal':
            total = sum(self.shares.values())
            for p in self.participants:
                splits[p] = round(self.amount * (self.shares[p] / total), 2)
        elif self.split_type == 'percent':
            for p in self.participants:
                splits[p] = round(self.amount * (self.shares[p] / 100), 2)
        return splits


class Debt:
    def __init__(self, debtor, creditor, amount):
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount


class Group:
    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.expenses = []
        self.debts = []

    def add_expense(self, expense):
        self.expenses.append(expense)
        self.recalculate_debts(expense)

    def recalculate_debts(self, expense):
        payer = expense.payer
        for user, share in expense.splits.items():
            if user == payer:
                continue
            self._add_debt(user, payer, share)
        self._simplify_debts()

    def _add_debt(self, debtor, creditor, amount):
        for d in self.debts:
            if d.debtor == debtor and d.creditor == creditor:
                d.amount += amount
                return
            elif d.debtor == creditor and d.creditor == debtor:
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
        change = True
        while change:
            change = False
            for d1 in list(self.debts):
                for d2 in list(self.debts):
                    if d1 != d2 and d1.creditor == d2.debtor:
                        if d1.debtor == d2.creditor:
                            continue
                        amount = min(d1.amount, d2.amount)
                        self._add_debt(d1.debtor, d2.creditor, amount)
                        d1.amount -= amount
                        d2.amount -= amount
                        change = True
                        if d1.amount <= 0:
                            if d1 in self.debts:
                                self.debts.remove(d1)
                        if d2.amount <= 0:
                            if d2 in self.debts:
                                self.debts.remove(d2)
                        break
                if change:
                    break

    def show_debts(self):
        if not self.debts:
            print("No debts in this group.")
            return
        for d in self.debts:
            print(f"{d.debtor.name} owes {d.creditor.name} ₹{d.amount:.2f}")

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


class SplitSmartApp:
    def __init__(self):
        self.users = []
        self.groups = []

    def find_user(self, name):
        for u in self.users:
            if u.name == name:
                return u
        return None

    def find_group(self, name):
        for g in self.groups:
            if g.name == name:
                return g
        return None
    
## added function to export data to JSON (Optional)

    def to_json(self):
        data = {
            "users": [
                {"name": u.name, "email": u.email}
                for u in self.users
            ],
            "groups": [
                {
                    "name": g.name,
                    "members": [m.name for m in g.members],
                    "expenses": [
                        {
                            "description": e.description,
                            "amount": e.amount,
                            "payer": e.payer.name,
                            "participants": [p.name for p in e.participants],
                            "split_type": e.split_type,
                            "splits": {p.name: s for p, s in e.splits.items()}
                        }
                        for e in g.expenses
                    ],
                    "debts": [
                        {"debtor": d.debtor.name, "creditor": d.creditor.name, "amount": d.amount}
                        for d in g.debts
                    ]
                }
                for g in self.groups
            ]
        }
        return json.dumps(data, indent=4)


    def add_user(self):
        name = input("Enter user name: ")
        email = input("Enter email: ")
        if self.find_user(name):
            print("User already exists.")
            return
        self.users.append(User(name, email))
        print("User added successfully!")

    def create_group(self):
        name = input("Enter group name: ")
        members_input = input("Add members (comma separated): ").split(',')
        members = []
        for m in members_input:
            u = self.find_user(m.strip())
            if u:
                members.append(u)
        if not members:
            print("No valid members found.")
            return
        self.groups.append(Group(name, members))
        print("Group created successfully!")

    def add_expense(self):
        gname = input("Enter group name: ")
        group = self.find_group(gname)
        if not group:
            print("Group not found.")
            return
        desc = input("Enter expense description: ")
        amount = float(input("Enter total amount: "))
        payer_name = input("Who paid? ")
        payer = self.find_user(payer_name)
        members_input = input("Enter participants (comma separated): ").split(',')
        participants = [self.find_user(m.strip()) for m in members_input if self.find_user(m.strip())]
        split_type = input("Split type (equal / unequal / percent): ").lower()
        shares = {}
        if split_type in ['unequal', 'percent']:
            for p in participants:
                val = float(input(f"Enter {'amount' if split_type == 'unequal' else 'percent'} for {p.name}: "))
                shares[p] = val
        expense = Expense(desc, amount, payer, participants, split_type, shares)
        group.add_expense(expense)
        print("Expense recorded successfully!")

    def view_debts(self):
        gname = input("Enter group name: ")
        group = self.find_group(gname)
        if not group:
            print("Group not found.")
            return
        group.show_debts()

    def settle_up(self):
        gname = input("Enter group name: ")
        group = self.find_group(gname)
        if not group:
            print("Group not found.")
            return
        payer = input("Payer name: ")
        receiver = input("Receiver name: ")
        amount = float(input("Enter amount to settle: "))
        group.settle_up(payer, receiver, amount)
        print("Settlement recorded.")

    def run(self):
        while True:
            print("\nSplitSmart Menu")
            print("1. Add User")
            print("2. Create Group")
            print("3. Add Expense")
            print("4. View Debts")
            print("5. Settle Up")
            print("6. View JSON Summary")
            print("7. Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                self.add_user()
            elif choice == '2':
                self.create_group()
            elif choice == '3':
                self.add_expense()
            elif choice == '4':
                self.view_debts()
            elif choice == '5':
                self.settle_up()
            elif choice == '6':
                print(self.to_json())
            elif choice == '7':
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    app = SplitSmartApp()
    app.run()
