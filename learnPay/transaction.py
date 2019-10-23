#!/usr/bin/env python3

from datetime import datetime
from collections import namedtuple
from dataclasses import dataclass

# sender,sender_id,sender_country, recipient_id,recipient_country,date,amount,currency
# Steve,Steve,2019-09-12,323,USD

# {
#    sender: {},
#    recipient: {},
#    date: ...,
#    amount: ...,
#    currency: ...,
# }

class TransactionCollection(object):

    def __init__(self):
        self.transactions = {}

    def append(self, transaction):
        self.transactions[len(self.transactions)] = transaction
        return len(self.transactions) - 1

    def __len__(self):
        return len(self.transactions)

    def __getitem__(self, item):
        return self.transactions[item]

    def clear(self):
        self.transactions.clear()

'''@dataclass
class Transaction:
    sender: object
    recipient: object
    date: datetime
    amount: float
    currency: str
'''
class Transaction(namedtuple('Transaction', 'sender recipient date amount currency')):

    #TODO implement json using a defualt encoder
    # James's code example
    # def default_json_encoder(value):  # XXX
    #     if isinstance(value, (datetime, date)):
    #         return f'{value:%Y-%m-%d}'
    #     elif isinstance(value, deque):
    #         return list(value)
    #     elif isinstance(value, Currency):
    #         return value.name
    #     elif isinstance(value, Transaction):
    #         sender = value.sender.as_dict if value.sender else None
    #         recipient = value.recipient.as_dict if value.recipient else None
    #         return {**asdict(value), 'sender': sender, 'recipient': recipient}
    #     return dumps(value)

    def as_json(self):
        # is there an impact to importing libs at method level
        from json import dumps
        retDict = {
            "sender": self.sender.as_dict,
            "recipient": self.recipient.as_dict,
            "date":f'{self.date:%Y-%m-%d}',
            "amount": float(self.amount),
            "currency": self.currency
         }
        return dumps(retDict)

    @classmethod
    def from_csv(cls,sender, sender_id, sender_country, recipient, recipient_id, recipient_country, date, amount, currency):
        from learnPay.data import Accounts, DATETIME_FORMAT

        date = datetime.strptime(date, DATETIME_FORMAT)
        amount = float(amount)

        sender = Accounts.get(int(sender_id))
        recipient = Accounts.get(int(recipient_id))
        return cls(sender,recipient,date,amount,currency)


    @classmethod
    def from_json(cls, parsed_json):
        from learnPay.data import Accounts, DATETIME_FORMAT
        sender = Accounts.get((parsed_json['sender']['id']))
        recipient = Accounts.get(parsed_json['recipient']['id'])
        amount = parsed_json.get('amount')
        currency = parsed_json.get('currency')
        date = datetime.strptime(parsed_json.get('date'), DATETIME_FORMAT)

        return cls(sender, recipient, date, amount, currency)
