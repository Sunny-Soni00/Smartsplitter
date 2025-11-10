class Expense:
    def __init__(self, description, amount, payer, participants, split_type, shares=None):
        self.description = description
        self.amount = amount
        self.payer = payer
        self.participants = participants
        self.split_type = split_type
        self.shares = shares or {}
        self.splits = self._calculate_splits()

    def _calculate_splits(self):
        n = len(self.participants)
        splits = {}
        if self.split_type == 'equal':
            share = round(self.amount / n, 2)
            for p in self.participants:
                splits[p] = share
        elif self.split_type == 'unequal':
            total = sum(self.shares.values())
            for p in self.participants:
                splits[p] = round(self.amount * (self.shares.get(p, 0) / total), 2)
        elif self.split_type == 'percent':
            for p in self.participants:
                splits[p] = round(self.amount * (self.shares.get(p, 0) / 100), 2)
        return splits