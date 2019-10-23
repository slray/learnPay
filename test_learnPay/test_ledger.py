import unittest

from learnPay.ledger import Ledger

class LedgerTestCase(unittest.TestCase):
    def setUp(self):
        import json
        from learnPay.account import Account
        from learnPay.data import Accounts
        data_path = 'data/balances.json'
        f = open(data_path).read()
        for account in json.loads(f):
            ident = account.get('id')
            Accounts[ident] = Account.from_json(account)
        pass

    def test_ofac_sanction(self):
        import json
        from learnPay.transaction import Transaction
        json_blob = '''{
                            "sender": {
                                "name": "Borys",
                                "id": 3,
                                "country": "North Korea"
                            },
                            "recipient": {
                                "name": "Steve",
                                "id": 4,
                                "country": "Spain"
                            },
                            "date": "2019-10-13",
                            "amount": 10.00,
                            "currency": "DKK"
                        }'''
        parsed_josn = json.loads(json_blob)

        transaction = Transaction.from_json(parsed_josn)

        self.assertEqual(transaction.sender.name, 'Borys')
        self.assertEqual(transaction.sender.ident, 3)
        self.assertEqual(transaction.sender.country, 'North Korea')
        self.assertEqual(transaction.recipient.name, 'Steve')
        self.assertEqual(transaction.recipient.ident, 4)
        self.assertEqual(transaction.recipient.country, 'Spain')
        self.assertEqual(transaction.amount, float('10.00'))
        self.assertEqual(transaction.currency, 'DKK')

        transanction_ofca_blocked = Ledger.is_transaction_sanctioned(transaction)

        self.assertTrue(transanction_ofca_blocked)

    def test_over_limit(self):
        import json
        from learnPay.transaction import Transaction
        transaction_limit = 5
        json_blob = '''{
                            "sender": {
                                "name": "Steve",
                                "id": 4,
                                "country": "United States"
                            },
                            "recipient": {
                                "name": "John",
                                "id": 6,
                                "country": "Canada"
                            },
                            "date": "2019-10-13",
                            "amount": 10.00,
                            "currency": "CHF"
                        }'''
        parsed_josn = json.loads(json_blob)

        transaction = Transaction.from_json(parsed_josn)


        for _ in range(transaction_limit):
            Ledger.process_transaction(transaction)

        transaction_limit_blocked = Ledger.too_many_outbound_transactions(transaction)
        self.assertTrue(transaction_limit_blocked)


if __name__ == '__main__':
    unittest.main()
