import unittest
from learnPay.account import Account
import json

class AccountTestCase(unittest.TestCase):
    def test_from_json(self):
        json_blob = '''
                    {
                    "name": "Steve",
                    "country": "Spain",
                    "balances": {
                        "GBP":    100,
                        "EUR":     50,
                        "CHF": 500000
                    },
                    "transactions": []
                    }
                '''
        parsed_json = json.loads(json_blob)
        acnt = Account.from_json(parsed_json)
        self.assertEqual('Steve', acnt.name)
        self.assertEqual('Spain', acnt.country)
        self.assertEqual([], acnt.transactions)
        self.assertEqual({"GBP": 100,
                          "EUR": 50,
                          "CHF": 500000},
                         acnt.balances)
        currencies = ['GBP', 'EUR', 'CHF']
        currencies.sort()
        account_currencies = acnt.currencies
        account_currencies.sort()
        self.assertListEqual(account_currencies, currencies)

        as_json = acnt.as_json


    def test_is_self(self):
        from learnPay.data import Accounts
        json_blob = '''[
                    {
                    "id": 4,
                    "name": "Steve",
                    "country": "Spain",
                    "balances": {
                        "GBP":    100,
                        "EUR":     50,
                        "CHF": 500000
                    },
                    "transactions": []
                    }
                ]
                '''

        for account in json.loads(json_blob):
            ident = account.get('id')
            Accounts[ident] = Account.from_json(account)

        acnt = Accounts[4]

        self.assertEqual('Steve', acnt.name)
        self.assertEqual('Spain', acnt.country)
        self.assertEqual([], acnt.transactions)
        self.assertEqual({"GBP": 100,
                          "EUR": 50,
                          "CHF": 500000},
                         acnt.balances)
        is_self = acnt.is_self(4)
        self.assertTrue(is_self)

class AccountsTestCase(unittest.TestCase):

    def test_add_new_account(self):
        from learnPay.data import Accounts
        json_blob = '''[
                    {
                    "id": 4,
                    "name": "Steve",
                    "country": "Spain",
                    "balances": {
                        "GBP":    100,
                        "EUR":     50,
                        "CHF": 500000
                    },
                    "transactions": []
                    }
                ]
                '''

        for account in json.loads(json_blob):
            ident = account.get('id')
            Accounts[ident] = Account.from_json(account)

        acnt = Accounts[4]

        self.assertEqual('Steve', acnt.name)
        self.assertEqual('Spain', acnt.country)
        self.assertEqual([], acnt.transactions)
        self.assertEqual({"GBP": 100,
                          "EUR": 50,
                          "CHF": 500000},
                         acnt.balances)



if __name__ == '__main__':
    unittest.main()
