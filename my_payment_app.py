from learnPay.gendata import random_payment_generator
from learnPay.account import Account, Accounts
from learnPay.ledger import Ledger
from learnPay.data import FailedTransactions
import json


data_path = 'data/balances.json'

#replace this this a list comprehession
for account in json.loads(open(data_path).read()):
    ident = account.get('id')
    Accounts[ident] = Account.from_json(account)

transactions = random_payment_generator()
max = 5000

every = lambda g, n: zip(g, cycle([True] + [False] * (n-1)))

from itertools import islice, cycle
for trnx, debug in every( islice(transactions, max), 10):
    Ledger.process_transaction(trnx)
    if debug:
        print(trnx.as_json())

for account_id, account in Accounts.items():
    print(account.display_balance())
print(FailedTransactions())
