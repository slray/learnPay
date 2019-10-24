#!/usr/bin/env python3

from collections import namedtuple, defaultdict, deque
from random import randrange, choices, choice
from datetime import datetime, timedelta, date
from string import ascii_lowercase
from decimal import Decimal
from json import load
from transaction import Transaction, Currency, Balance, Account
from pathlib import Path

# sender,sender_id,sender_country,\
# recipient_id,recipient_country,date,amount,currency
# Steve,Steve,2019-09-12,323,USD

# {
#    sender: {},
#    recipient: {},
#    date: ...,
#    amount: ...,
#    currency: ...,
# }

def generate_random_transactions(accounts, *, refdate):
    while True:
        for _ in range(randrange(0, 1000)):
            refdate += timedelta(days=1)
            while True:
                sender, recipient = choices(list(accounts.values()), k=2)
                if sender is not recipient \
                   and any(bal > 0 for _, bal in sender.balances.items()):
                    break
            bals = sender.balances
            curr = choice([curr for curr, amt in bals.items() if amt > 0]) # XXX
            amt = randrange(0, bals[curr])
            pmt = Transaction(sender, recipient, refdate, amt, curr)
            accounts[recipient.ident].transactions.append(pmt)
            accounts[sender.ident].transactions.append(pmt) # XXX
            yield pmt

if __name__  == '__main__':
    with open('balances.json') as f:
        data = load(f)

    today = datetime.now().date()

    accounts = {(x:=Account.from_json(acct, refdate=today)).ident: x
                for acct in data}

    for pmt in generate_random_transactions(accounts, refdate=date(2019, 1, 1)):
        try:
            path = Path('transactions') / pmt.ident.decode('ascii')
            with open(path, 'w') as f:
                f.write(pmt.as_json)
            print(f'wrote to {path}')
            from time import sleep; sleep(.5)
        except BrokenPipeError:
            break
