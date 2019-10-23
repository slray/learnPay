from learnPay.transaction import TransactionCollection
from itertools import chain
from dataclasses import dataclass
from collections import namedtuple
from datetime import datetime

import json

Transactions = TransactionCollection()
ProcessedTransactions = []
InvalidTransactions = []
FraudTransactions = []
SanctionedTransactions = []
OverLimitTransactions = []
FailedTransactions = lambda: chain(InvalidTransactions, FraudTransactions,
                         SanctionedTransactions, OverLimitTransactions)

Accounts = {}

DATETIME_FORMAT = '%Y-%m-%d'
OFAC = json.loads(open('data/ofac.json').read())
Sanctions = json.loads(open('data/sanctions.json').read())


def init_data():
    Transactions.clear()
    Accounts.clear()
    FailedTransactions.clear()
    FraudTransactions.clear()



class intervaldict(dict):
    def __missing__(self, key):
        for (lower, upper), value in sorted(self.items()):
            if lower is None and upper is None:
                return value
            if lower is None and key < upper:
                return value
            if upper is None and lower <= key:
                return value
            if lower <= key < upper:
                return value
        raise KeyError(f'cannot find {key} in interval')

@dataclass
class Sanctions:
    region: str
    countries: list
    periods: list

    @classmethod
    def from_json(cls, data):
        periods = [Period.from_json(p) for p in data['sanctions']]
        return cls(data['region'], data['countries'], periods)

    def __getitem__(self, country):
        return intervaldict({(p.from_date, p.to_date): p
                             for p in self.periods
                             if p.country == country})

class Period(namedtuple('Period', 'country from_date to_date')):
    @classmethod
    def from_json(cls, data):
        from_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
        if 'end' in data:
            to_date = datetime.strptime(data['end'], '%Y-%m-%d').date()
        else:
            to_date = None
        return cls(data['country'], from_date, to_date)
Sanctions
