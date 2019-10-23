#!/usr/bin/env python3
from learnPay.data import Accounts
from learnPay.data import Transactions
from dataclasses import dataclass, asdict
from json import dumps

@dataclass
class Account:
    ident: int
    name: str
    country: str
    balances: dict
    transactions: list

    def add_balance(self, transaction):
        if not transaction.currency in self.balances.keys():
            self.balances[transaction.currency] = 0
        self.balances[transaction.currency] += transaction.amount

    def remove_balance(self, transaction):
        self.balances[transaction.currency] -= transaction.amount

    @property
    def currencies(self):
        return list(self.balances.keys())

    def display_balance(self):
        items = [f'{amount} {currency}' for amount,currency in self.balances.items()]
        retStr = '\n\t'.join(items)

        return f'{self.name} ' + retStr

    def process_transaction(self, transaction_id):
        self.transactions.append(transaction_id)
        transaction = Transactions[transaction_id]
        if self.is_self(transaction.sender.ident):
            self.remove_balance(transaction)
        else:
            self.add_balance(transaction)

    def is_self(self, sender_id):
        sender = Accounts.get(sender_id)
        return sender == self


    @property
    def as_json(self):
        retDict = asdict(self)
        retDict.pop('ident')
        return dumps({**retDict, 'id': self.ident})

    @property
    def as_dict(self):
        retDict = asdict(self)
        retDict.pop('balances')
        retDict.pop('ident')
        retDict.pop('transactions')
        return {**retDict, 'id': self.ident}

    @classmethod
    def from_json(cls, parsed_json):
        ident = parsed_json.get('id')
        name = parsed_json.get('name')
        country = parsed_json.get('country')
        balances = parsed_json.get('balances')
        transactions = parsed_json.get('transactions')
        return cls(ident, name, country, balances, transactions)













