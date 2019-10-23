import unittest
from learnPay import gendata
from learnPay.ledger import Ledger
from learnPay.data import Transactions, Accounts
from datetime import datetime
from decimal import Decimal


class TestGenData(unittest.TestCase):
    def setUp(self):
        import json
        from learnPay.account import Account
        data_path = 'data/balances.json'
        f = open(data_path).read()
        for account in json.loads(f):
            ident = account.get('id')
            Accounts[ident] = Account.from_json(account)
        pass
    def test_random_payment_generator(self):

        transactions = gendata.random_payment_generator()
        max_count = 3
        for trnx in transactions:
            self.assertTrue(trnx.sender.ident in Accounts.keys())
            self.assertTrue(trnx.sender.name in [v.name for k, v in Accounts.items()])
            self.assertTrue(trnx.sender.country in [v.country for k, v in Accounts.items()])
            self.assertTrue(trnx.recipient.ident in Accounts.keys())
            self.assertTrue(trnx.recipient.name in [v.name for k, v in Accounts.items()])
            self.assertTrue(trnx.recipient.country in [v.country for k, v in Accounts.items()])
            self.assertTrue(isinstance(trnx.amount, Decimal))
            self.assertTrue(isinstance(trnx.date, datetime))
            self.assertTrue(trnx.currency in trnx.sender.currencies)
            Ledger.process_transaction(trnx)

            if len(Transactions) > max_count:
                transactions.close()
            pass


if __name__ == '__main__':
    unittest.main()
