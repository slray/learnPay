import unittest

from learnPay.transaction import Transaction
from csv import reader
from io import StringIO


class TransactionTestCase(unittest.TestCase):

    def setUp(self):
        import json
        from learnPay.account import Account
        from learnPay.data import Accounts
        data_path = 'data/balances.json'
        f = open(data_path).read()
        for account in json.loads(f):
            ident = account.get('id')
            Accounts[ident] = Account.from_json(account)


    def test_from_csv(self):
        csv_line = StringIO('Becky,1,United States,Varsha,6,Australia,2019-10-13,10.00,USD\n')
        for fields in reader(csv_line):
            transaction = Transaction.from_csv(*fields)
            self.assertEqual(transaction.sender.name, 'Becky')
            self.assertEqual(transaction.sender.ident, 1)
            self.assertEqual(transaction.sender.country, 'United States')
            self.assertEqual(transaction.recipient.name, 'Varsha')
            self.assertEqual(transaction.recipient.ident, 6)
            self.assertEqual(transaction.recipient.country, 'Australia')
            self.assertEqual(transaction.amount, float('10.00'))
            self.assertEqual(transaction.currency, 'USD')



    def test_from_json(self):
        import json
        json_blob = '''{
            "sender": {
                "name": "Steve",
                "id": 4,
                "country": "Spain"
            },
            "recipient": {
                "name": "Varsha",
                "id": 6,
                "country": "Australia"
            },
            "date": "2019-10-13",
            "amount": 10.00,
            "currency": "USD"
        }'''
        parsed_josn = json.loads(json_blob)

        transaction = Transaction.from_json(parsed_josn)

        self.assertEqual(transaction.sender.name, 'Steve')
        self.assertEqual(transaction.sender.ident, 4)
        self.assertEqual(transaction.sender.country, 'Spain')
        self.assertEqual(transaction.recipient.name, 'Varsha')
        self.assertEqual(transaction.recipient.ident, 6)
        self.assertEqual(transaction.recipient.country, 'Australia')
        self.assertEqual(transaction.amount, float('10.00'))
        self.assertEqual(transaction.currency, 'USD')

    def test_to_json(self):
        import json
        json_blob = '''{
                    "sender": {
                        "name": "Steve",
                        "id": 4,
                        "country": "Spain"
                    },
                    "recipient": {
                        "name": "Varsha",
                        "id": 6,
                        "country": "Australia"
                    },
                    "date": "2019-10-13",
                    "amount": 10.00,
                    "currency": "USD"
                }'''
        parsed_josn = json.loads(json_blob)

        transaction = Transaction.from_json(parsed_josn)

        self.assertEqual(transaction.sender.name, 'Steve')
        self.assertEqual(transaction.sender.ident, 4)
        self.assertEqual(transaction.sender.country, 'Spain')
        self.assertEqual(transaction.recipient.name, 'Varsha')
        self.assertEqual(transaction.recipient.ident, 6)
        self.assertEqual(transaction.recipient.country, 'Australia')
        self.assertEqual(transaction.amount, float('10.00'))
        self.assertEqual(transaction.currency, 'USD')


        as_json = transaction.as_json()

        transaction = Transaction.from_json(
            json.loads(as_json
            )
        )

        self.assertEqual(transaction.sender.name, 'Steve')
        self.assertEqual(transaction.sender.ident, 4)
        self.assertEqual(transaction.sender.country, 'Spain')
        self.assertEqual(transaction.recipient.name, 'Varsha')
        self.assertEqual(transaction.recipient.ident, 6)
        self.assertEqual(transaction.recipient.country, 'Australia')
        self.assertEqual(transaction.amount, float('10.00'))
        self.assertEqual(transaction.currency, 'USD')



if __name__ == '__main__':
    unittest.main()
