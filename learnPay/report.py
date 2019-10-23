#!/usr/bin/env python3

from learnPay.ledger import Ledger
from learnPay.transaction import Transaction
from csv import reader

# abcd 100 USD
#      200 EUR
# wzyx 90 USD
#      30 JPY

data_path = 'data/data.csv'

def get_report():
    with open(data_path) as f:
        for fields in reader(f):
            #name, date, amount, currency = fields
            Ledger.process_record(Transaction.from_csv(*fields))

    output_file = []
    for user, account in Ledger.accounts.items():
        output_file.append(account.display_balance())


if __name__ == 'main':
    get_report()

