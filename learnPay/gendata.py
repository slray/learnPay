#!/usr/bin/env python3

from random import randrange, choice
from datetime import datetime, timedelta
from decimal import Decimal
from learnPay.transaction import Transaction
from learnPay.account import Accounts
import csv

# sender,sender_id, sender_country, recipient, recipient_id,recipient_country,date,amount,currency
# Steve,Steve,2019-09-12,323,USD

# {
#    sender: {},
#    recipient: {},
#    date: ...,
#    amount: ...,
#    currency: ...,
# }

def time_walk(refdate=datetime.now()):
    while True:
        yield refdate
        time_step = {
            "milliseconds":randrange(0, 1000),
            "seconds":randrange(0, 60),
            "minutes":randrange(0, 60),
            "hours": randrange(0, 12)
        }
        refdate += timedelta(**time_step)


def random_payment_generator():
    #currencies = ['USD', 'EUR', 'JPY', 'CHF']
    time_walker = time_walk()
    while True:
        sender = Accounts[choice(list(Accounts.keys()))]
        recipient = Accounts[choice(list(Accounts.keys()))]
        while sender == recipient:
            recipient = Accounts[choice(list(Accounts.keys()))]
        currency = choice(sender.currencies)
        date = next(time_walker) # called next on generator
        balance_in_cents = int(sender.balances[currency]*100)
        amount  = Decimal(randrange(0,balance_in_cents+1))/100

        transaction = Transaction(sender, recipient, date, amount, currency)
        yield transaction
    













