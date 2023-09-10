import json

from crypto_util import calculate_fee, MAX_BLOCK_TRANSACTIONS
from transaction import Transaction
from random import randint, sample, choice


class TransactionManager:
    def __init__(self, key_manager, blockchain):
        self.keyManager = key_manager
        self.blockchain = blockchain
        self.transaction_pool = []

    # Dodanie nowej transakcji do transaction pool
    def add_transaction(self, transaction):
        self.transaction_pool.append(transaction)

    def generate_transaction(self):
        input = self.choose_unspent_output()
        receiver_ip = self.keyManager.choose_node()
        sender_public_key = self.keyManager.get_my_public_key()
        if input.amount - calculate_fee(input.amount) > 1:
            amount = randint(1, input.amount - calculate_fee(input.amount))
            transaction = Transaction.create(input, receiver_ip, sender_public_key, amount)
            self.keyManager.sign(transaction)
            self.add_transaction(transaction)
            return transaction
        else:
            return None

    def choose_transactions(self):
        max_number = min(MAX_BLOCK_TRANSACTIONS, len(self.transaction_pool))
        chosen_number_of_transactions = randint(1, max_number)
        return sample(self.transaction_pool, chosen_number_of_transactions)

    def pop_transactions(self):
        chosen_transactions = self.choose_transactions()
        transactions_dict = [transaction.to_dict() for transaction in chosen_transactions]
        transactions_dict.append(self.add_coinbase_transaction(chosen_transactions))
        return transactions_dict

    def filter_transactions(self):
        main_branch_transactions, outside_transactions = self.blockchain.get_main_and_outside_transactions()
        for main_branch_transaction in main_branch_transactions:
            if main_branch_transaction.is_in_list(self.transaction_pool):
                self.transaction_pool.remove(main_branch_transaction)
        for outside_transaction in outside_transactions:
            if not outside_transaction.is_in_list(self.transaction_pool):
                self.transaction_pool.append(outside_transaction)

    def print_transactions(self):
        transactions_dict = [transaction.to_dict() for transaction in self.transaction_pool]
        print(json.dumps(transactions_dict, indent=4))

    def get_available_balance(self):
        return sum(output.amount for output in self.get_available_outputs())

    def print_balance(self):
        print(f'Current available balance = {self.get_available_balance()})')

    def get_available_outputs(self):
        available_unspent_outputs = [output for output in self.blockchain.get_unspent_outputs(
            self.keyManager.get_my_ip(),
            self.blockchain.main_branch)]
        for transaction in self.transaction_pool:
            if transaction.input.is_in_list(available_unspent_outputs):
                available_unspent_outputs.remove(transaction.input)
        return available_unspent_outputs

    def choose_unspent_output(self):
        unspent_output = choice(self.get_available_outputs())
        return unspent_output

    def add_coinbase_transaction(self, chosen_transactions):
        ip, public_key = self.keyManager.get_my_ip(), self.keyManager.get_my_public_key()
        coinbase_transaction = Transaction.create_coinbase(ip, public_key, chosen_transactions)
        self.keyManager.sign(coinbase_transaction)
        return coinbase_transaction.to_dict()

    def is_transaction_pool_empty(self):
        return len(self.transaction_pool) == 0
