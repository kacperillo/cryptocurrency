import hashlib
import json
from transaction import Transaction


class Block:

    def __init__(self, previous_header, nonce, header, transactions_dict):
        self.previous_header = previous_header  # hash bloku poprzedniego
        self.nonce = nonce  # nonce
        self.header = header  # hash bloku obecnego
        self.transactions = [Transaction(**transaction_dict) for transaction_dict in transactions_dict]

    # Zwrócenie danych transakcji w postaci listy
    def get_transactions_dict(self):
        return [transaction.to_dict() for transaction in self.transactions]

    # Wyznacz hash bloku
    def __hash__(self):
        return hashlib.sha256(self.previous_header.encode('utf-8')
                              + str(self.nonce).encode('utf-8')
                              + str(self.get_transactions_dict()).encode('utf-8')).hexdigest()

    def get_winner_port(self):
        for transaction in self.transactions:
            if transaction.input is None and len(transaction.outputs) == 1:
                return transaction.outputs[0].get_owner_port()

    def __eq__(self, other):
        if self.previous_header != other.previous_header or \
                self.nonce != other.nonce or \
                self.header != other.header:
            return False
        return True

    def is_in_list(self, blocks_list):
        for block in blocks_list:
            if block.__eq__(self):
                return True
        return False

    # Konwersja do słownika
    def to_dict(self):
        return {'previous_header': self.previous_header,
                'nonce': self.nonce,
                'header': self.header,
                'transactions_dict': self.get_transactions_dict()}

    # Konwersja do json
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
