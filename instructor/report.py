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
from pathlib import Path
from trio import run, open_nursery, sleep as trio_sleep

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

class TaskSet(namedtuple('TaskSet', 'tasks done')):
    @property
    def todo(self):
        return self.tasks - self.done

FILES        = TaskSet({*''}, {*''})
TRANSACTIONS = TaskSet({*''}, {*''})
FLAGGED      = {*''}

async def reader():
    while True:
        FILES.tasks.update(
            {p for p in Path('transactions/').iterdir() if p.is_file()}
        )
        await trio_sleep(0)

async def processor(accounts, today):
    while True:
        if FILES.todo:
            path = FILES.todo.pop()
            with open(path) as f: # XXX
                data = load(f)
            tx = Transaction.from_json(data, accounts=accounts, refdate=today)
            accounts[tx.sender.ident].transactions.append(tx)
            accounts[tx.recipient.ident].transactions.append(tx)
            TRANSACTIONS.todo.add(tx)
            FILES.done.add(tx)
        await trio_sleep(0)

async def validator(sanctions):
    while True:
        if TRANSACTIONS.todo:
            tx = TRANSACTIONS.todo.pop()
            try:
                s = sanctions[tx.sender.country][tx.recipient.country][tx.date]
                FLAGGED.add(tx)
            except KeyError:
                pass
            TRANSACTIONS.done.add(tx)
        await trio_sleep(0)

async def reporter(accounts):
    while True:
        print('\033c')
        for acct in sorted(accounts.values(), key=lambda acct: acct.name):
            min_dates = {curr: min(p.date for p in ps)
                         for curr, ps in acct.by_currency.items()}
            max_dates = {curr: max(p.date for p in ps)
                         for curr, ps in acct.by_currency.items()}
            bals = [f'{amt:10.2f} {Symbols[curr]} ({curr.name})'
                    f' ({min_dates[curr]:%Y-%m-%d} ~ {max_dates[curr]:%Y-%m-%d})'
                    for curr, amt in sorted(acct.balances.items())]
            pred = lambda _, c=chain([False], repeat(True)): next(c) # XXX
            bals = indent('\n'.join(bals), ' ' * (2 + len(f'{acct.name:<10}')), pred)
            print(f'{acct.name:<10}  {bals}')
            break

        print('Flagged Transactions'.center(50, '-'))
        for tx in FLAGGED:
            print(f'{tx.date:%Y-%m-%d} {tx.sender.name} → {tx.recipient.name}')
            print(f'           region   = {tx.sender.country} → {tx.recipient.country}')
            print(f'           date     = {tx.date}')
            print(f'           amount   = {tx.amount}')
            print(f'           currency = {tx.currency}')
        await trio_sleep(1)

async def main():
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

    async with open_nursery() as n:
        n.start_soon(reader)
        n.start_soon(processor, accounts, today)
        n.start_soon(validator, sanctions)
        n.start_soon(reporter, accounts)

if __name__ == '__main__':
    run(main)
