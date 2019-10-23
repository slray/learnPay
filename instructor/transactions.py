from enum import Enum, auto
from datetime import datetime, date
from decimal import Decimal
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from json import dumps
from functools import total_ordering

def default_json_encoder(value): # XXX
    if isinstance(value, (datetime, date)):
        return f'{value:%Y-%m-%d}'
    elif isinstance(value, deque):
        return list(value)
    elif isinstance(value, Currency):
        return value.name
    elif isinstance(value, Transaction):
        sender = value.sender.as_dict if value.sender else None
        recipient = value.recipient.as_dict if value.recipient else None
        return {**asdict(value), 'sender': sender, 'recipient': recipient}
    return dumps(value)

@total_ordering
class Currency(Enum):
    CHF = auto()
    DKK = auto()
    GBP = auto()
    EUR = auto()
    INR = auto()
    JPY = auto()
    USD = auto()

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other): # XXX
        return self.name < other.name

    def __hash__(self):
        return hash(self.value)

Symbols = defaultdict(lambda: '\N{currency sign}', {
    Currency.INR: '\N{tamil rupee sign}',
    Currency.EUR: '\N{euro sign}',
    Currency.JPY: '\N{yen sign}',
    Currency.USD: '$',
    Currency.GBP: '\N{pound sign}',
})

@dataclass # XXX
class Transaction:
    sender: object
    recipient: object
    date: date
    amount: Decimal
    currency: Currency

    @classmethod
    def from_csv(cls, fields):
        sender, recipient, date, amount, currency = fields
        send_date = datetime.strptime(date, '%Y-%m-%d').date()
        amount = Decimal(amount)
        currency = Currency.__members__[currency]
        return cls(sender, recipient, send_date, amount, currency)

    @classmethod
    def from_json(cls, data, accounts={}, *, refdate): # XXX: accounts
        if data['sender']['id'] not in accounts:
            sender = Account.from_json(data['sender'], refdate=refdate)
            accounts[sender.ident] = sender
        sender = accounts[data['sender']['id']]
        if data['recipient']['id'] not in accounts:
            recipient = Account.from_json(data['recipient'], refdate=refdate)
            accounts[recipient.ident] = sender
        recipient = accounts[data['recipient']['id']]
        send_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        amount = data['amount']
        currency = Currency.__members__[data['currency']]
        return cls(sender, recipient, send_date, amount, currency)

    @property
    def as_json(self):
        return dumps(self, default=default_json_encoder)

    @property
    def as_csv(self):
        return f'{self.sender},{self.recipient},{self.date:%Y-%m-%d},{self.amount:.2f},{self.currency}'

class Balance(Transaction):
    @classmethod
    def from_json(cls, account, currency, amount, *, refdate):
        currency = Currency.__members__[currency]
        return cls(None, account, refdate, amount, currency)

@dataclass
class Account:
    ident: int
    name: str
    country: str
    transactions: deque

    @classmethod
    def from_json(cls, data, *, refdate): # XXX: kw-only
        ident = data['id']
        name = data['name']
        country = data['country']
        transactions = deque(Transaction.from_json(x)
                             for x in data.get('transactions', []))
        rv = cls(ident, name, country, transactions)
        balances = [Balance.from_json(rv, k, v, refdate=refdate)
                    for k, v in data.get('balances', {}).items()]
        rv.transactions.extendleft(balances)
        return rv

    @property
    def by_currency(self):
        by_curr = defaultdict(list)
        for pmt in self.transactions:
            by_curr[pmt.currency].append(pmt)
        return by_curr

    @property
    def balances(self):
        bals = defaultdict(Decimal)
        for curr, pmts in self.by_currency.items():
            bals[curr] = sum(p.amount for p in pmts if p.recipient is self) \
                       + sum(-p.amount for p in pmts if p.sender is self)
        return bals

    @property
    def as_json(self):
        data = asdict(self)
        data.pop('ident')
        return dumps({**data, 'id': self.ident}, default=default_json_encoder)

    # XXX
    @property
    def as_dict(self):
        data = asdict(self)
        data.pop('ident')
        data.pop('transactions')
        return {**data, 'id': self.ident}

    def __repr__(self):
        return f'{type(self).__name__}({self.ident!r}, {self.name!r}, {self.country!r}, [...])'
