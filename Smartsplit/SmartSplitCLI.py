import json
from User import User
from Group import Group
from Expense import Expense

class SplitSmartApp:
    def __init__(self):
        self.users = []
        self.groups = []

    def find_user(self, name):
        return next((u for u in self.users if u.name == name), None)

    def find_group(self, name):
        return next((g for g in self.groups if g.name == name), None)

    def to_json(self):
        data = {
            "users": [{"name": u.name, "email": u.email} for u in self.users],
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
                            "splits": {p.name: s for p, s in e.splits.items()},
                        }
                        for e in g.expenses
                    ],
                    "debts": [{"debtor": d.debtor.name, "creditor": d.creditor.name, "amount": d.amount} for d in g.debts],
                }
                for g in self.groups
            ],
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
        members_input = input("Add members (comma separated): ").split(",")
        members = [self.find_user(m.strip()) for m in members_input if self.find_user(m.strip())]
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
        members_input = input("Enter participants (comma separated): ").split(",")
        participants = [self.find_user(m.strip()) for m in members_input if self.find_user(m.strip())]
        split_type = input("Split type (equal / unequal / percent): ").lower()
        shares = {}
        if split_type in ["unequal", "percent"]:
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
    SplitSmartApp().run()