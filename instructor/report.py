#!/usr/bin/env python3

from csv import reader
from collections import defaultdict, namedtuple
from enum import Enum, auto
from textwrap import dedent, indent
from json import load
from datetime import datetime, date
from itertools import chain, repeat
from dataclasses import dataclass
from itertools import islice, tee

from transaction import Transaction, Symbols, Account

# name: total in each currency

# Name: 100 USD (from-date ... to-date)
#       125 EUR (from-date ... to_date)
# Name: 90 USD
#       30 JPY

# -> JSON output in the form of balances.json

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

nwise = lambda g, n: zip(*(islice(g, i, None) for i, g in enumerate(tee(g,n))))

if __name__ == '__main__':
    today = datetime.now().date()

    with open('ofac.json') as f:
        data = load(f)
    sanctions = defaultdict(
        lambda: Sanctions(None, None, []),
        {
            'United States': Sanctions(None, ['United States'],
                                       [Period.from_json(p) for p in data]),
        }
     )

    with open('balances.json') as f: # XXX
        data = load(f)
    accounts = {(x:=Account.from_json(acct, refdate=today)).ident: x
                for acct in data}

    with open('transactions.big.json') as f: # XXX
        data = load(f)
    transactions = [Transaction.from_json(x, accounts=accounts, refdate=today) for x in data]

    for tx in transactions:
        accounts[tx.sender.ident].transactions.append(tx)
        accounts[tx.recipient.ident].transactions.append(tx)

    flagged = []
    for tx in transactions:
        try:
            s = sanctions[tx.sender.country][tx.recipient.country][tx.date]
            flagged.append(tx)
        except KeyError:
            pass
    for acct in accounts.values():
        for txs in nwise(sorted(acct.transactions, key=lambda tx: tx.date), 5):
            first, *_, last = txs
            if not all(tx.sender is acct for tx in txs):
                continue
            if (last.date - first.date).days < 10:
                for tx in txs:
                    print(tx.sender.name, tx.recipient.name, tx.amount)

    # for acct in sorted(accounts.values(), key=lambda acct: acct.name):
    #     min_dates = {curr: min(p.date for p in ps)
    #                  for curr, ps in acct.by_currency.items()}
    #     max_dates = {curr: max(p.date for p in ps)
    #                  for curr, ps in acct.by_currency.items()}
    #     bals = [f'{amt:10.2f} {Symbols[curr]} ({curr.name})'
    #             f' ({min_dates[curr]:%Y-%m-%d} ~ {max_dates[curr]:%Y-%m-%d})'
    #             for curr, amt in sorted(acct.balances.items())]
    #     pred = lambda _, c=chain([False], repeat(True)): next(c) # XXX
    #     bals = indent('\n'.join(bals), ' ' * (2 + len(f'{acct.name:<10}')), pred)
    #     print(f'{acct.name:<10}  {bals}')
