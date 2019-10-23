#!/usr/bin/env python3

from learnPay.data import Transactions, InvalidTransactions,  ProcessedTransactions, SanctionedTransactions, OverLimitTransactions, FailedTransactions, OFAC, DATETIME_FORMAT
from datetime import datetime


class Ledger(object):

    @classmethod
    def process_transaction(cls, transaction):
        transaction_id = Transactions.append(transaction)
        if Ledger.is_transaction_invalid(transaction):
            InvalidTransactions.append(transaction_id)
        elif Ledger.is_transaction_sanctioned(transaction):
            SanctionedTransactions.append(transaction_id)
        elif Ledger.too_many_outbound_transactions(transaction):
            OverLimitTransactions.append(transaction_id)
        else:
            transaction.sender.process_transaction(transaction_id)
            transaction.recipient.process_transaction(transaction_id)
            ProcessedTransactions.append(transaction_id)


    @staticmethod
    def is_transaction_invalid(transaction):
        balances = transaction.sender.balances
        currency_balance =  balances[transaction.currency]
        return transaction.amount >currency_balance

    @staticmethod
    def is_transaction_sanctioned(transaction):
        from learnPay.data import OFAC

        #can clean up with list comperhension and :=
        ofac = None
        for country in OFAC:
            if country.get("country") in [transaction.sender.country, transaction.recipient.country] :
                ofac = country
        if ofac is None:
            return False

        #TODO clean up using intervaldict example code in learnPay/data

        start_date = datetime.strptime(ofac.get("start"), DATETIME_FORMAT)
        end_date = None
        if 'end' in ofac:
            end_date = datetime.strptime(ofac.get("end"), DATETIME_FORMAT)

        if transaction.date >= start_date:
            if end_date is None:
                return  True
            if end_date > transaction.date:
                return True
        return False

    @staticmethod
    def too_many_outbound_transactions(transaction, limit=5):
        if len(transaction.sender.transactions) < limit:
            return False

        #TODO check if transactions are with in time interval
        last_n_transactions = [Transactions[ident] for ident in transaction.sender.transactions[:-5]]

        for trxn in last_n_transactions:
            if trxn.recipient == transaction.sender:
                return False
        return True

fraud_rules = {
    'ofac':Ledger.is_transaction_sanctioned,
    'long_sequences':Ledger.too_many_outbound_transactions
}











