import json


class Output:
    def __init__(self, transaction_id, owner_ip, amount: int):
        self.transaction_id = transaction_id
        self.owner_ip = owner_ip
        self.amount = amount

    def __eq__(self, other):
        if self.transaction_id != other.transaction_id or \
                self.owner_ip != other.owner_ip or \
                self.amount != other.amount:
            return False
        return True

    def is_in_list(self, outputs_list):
        for output in outputs_list:
            if output.__eq__(self):
                return True
        return False

    def __str__(self):
        return self.transaction_id + self.owner_ip + str(self.amount)

    def get_owner_port(self):
        return self.owner_ip.split(':')[-1]

    def to_dict(self):
        return {'transaction_id': self.transaction_id,
                'owner_ip': self.owner_ip,
                'amount': self.amount}

    def to_json(self):
        return json.dumps(self.to_dict())
