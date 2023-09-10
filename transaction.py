import json
import uuid
from crypto_util import REWARD, calculate_fee, compute_hash
from output import Output


class Transaction:

    def __init__(self, transaction_id, input_dict, outputs_dict, fee: int, sender_public_key, signature):
        self.transaction_id = transaction_id
        self.input = Output(**input_dict) if input_dict is not None else None
        self.outputs = [Output(**output_dict) for output_dict in outputs_dict]
        self.fee = fee
        self.public_key = sender_public_key
        self.signature = signature

    def set_signature(self, signature):
        self.signature = signature

    @classmethod
    def create(cls, unspent_output, receiver_ip, sender_public_key, amount):
        transaction_id = str(uuid.uuid1())
        input = unspent_output
        outputs = [Output(transaction_id, receiver_ip, amount)]
        fee = calculate_fee(amount)
        change = input.amount - amount - fee
        if change > 0:
            outputs.append(
                Output(transaction_id, unspent_output.owner_ip, change))
        outputs_dict = [output.to_dict() for output in outputs]
        return cls(transaction_id, input.to_dict(), outputs_dict, fee, sender_public_key, '')

    @classmethod
    def create_coinbase(cls, miner_ip, miner_public_key, transactions):
        transaction_id = str(uuid.uuid1())
        amount = sum([transaction.fee for transaction in transactions]) + REWARD
        outputs = [Output(transaction_id, miner_ip, amount)]
        outputs_dict = [output.to_dict() for output in outputs]
        fee = 0
        return cls(transaction_id, None, outputs_dict, fee, miner_public_key, '')

    def get_outputs_amount(self):
        return sum(output.amount for output in self.outputs)

    def __eq__(self, other):
        if self.transaction_id != other.transaction_id or \
                not self.input.__eq__(other.input) or \
                self.fee != other.fee or \
                self.public_key != other.public_key or \
                self.signature != other.signature:
            return False
        for i, output in enumerate(self.outputs):
            if not output.__eq__(other.outputs[i]):
                return False
        return True

    def is_in_list(self, transaction_list):
        for transaction in transaction_list:
            if transaction.__eq__(self):
                return True
        return False

    def __str__(self):
        outputs_string = ''
        for output in self.outputs:
            outputs_string += output.__str__()
        input_string = self.input.__str__() if self.input is not None else 'null'
        return self.transaction_id + input_string + outputs_string + str(self.fee) + self.public_key

    def __hash__(self):
        return compute_hash(self.__str__())

    def get_sender_port(self):
        return self.input.get_owner_port() if self.input is not None else 'null'

    def is_coinbase(self):
        return self.input is None

    # Konwersja do słownika
    def to_dict(self):
        return {'transaction_id': self.transaction_id,
                'input_dict': self.input.to_dict() if self.input is not None else None,
                'outputs_dict': [output.to_dict() for output in self.outputs],
                'fee': self.fee,
                'sender_public_key': self.public_key,
                'signature': self.signature}

    # Konwersja do json
    def to_json(self):
        return json.dumps(self.to_dict())
