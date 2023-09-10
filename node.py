from threading import Thread, Lock
from time import sleep
import requests
from colorama import Fore, Style
from random import random, randint, choice

from block import Block
from blockchain import Blockchain
from crypto_util import MIN_FEE, get_identity_json
from key_manager import KeyManager
from miner import Miner
from transaction import Transaction
from transaction_manager import TransactionManager
from validator import validate_block, validate_transaction


class Node:

    def __init__(self, port):
        self.__PORT = port
        self.__IP = 'http://127.0.0.1:' + self.__PORT
        self.keyManager = KeyManager(self.__IP, self.__PORT)
        self.blockchain = Blockchain()
        self.miner = Miner()
        self.transactionManager = TransactionManager(self.keyManager, self.blockchain)
        self.lock = Lock()
        print(Fore.GREEN + f'Node started on port: {self.__PORT}' + Style.RESET_ALL)

    def get_port(self):
        return self.__PORT

    '''--------------------------------------CONNECTION---------------------------------------'''

    # Połączenie do znanego node'a
    def connect(self, known_ip_addr):
        response = self.__send_request(
            url=known_ip_addr + '/new-node',
            json=self.keyManager.get_my_identity_json())
        if response.status_code == 201:
            self.keyManager.set_nodes(response.json())
        else:
            print(f'Failed with {response.status_code}')

    # Dodanie klucza publicznego nowego node'a do listy
    def add_new_node(self, new_public_key, new_ip):
        self.keyManager.add_node(new_public_key, new_ip)
        print(Fore.CYAN + f'New node {new_ip} has been added' + Style.RESET_ALL)
        self.broadcast_new_node(new_public_key, new_ip)

    # Zaktualizowanie listy połączonych nodes
    def update_nodes_list(self, new_public_key, new_ip):
        self.keyManager.add_node(new_public_key, new_ip)
        print(Fore.CYAN + 'List of nodes has been updated' + Style.RESET_ALL)

    def get_nodes_list_json(self):
        return self.keyManager.get_nodes_json()

    def print_nodes_list(self):
        print(self.get_nodes_list_json())

    '''--------------------------------------TRANSACTIONS---------------------------------------'''
    # Sprawdzenie salda
    def check_balance(self):
        self.transactionManager.print_balance()

    # Dodanie transakcji do transkaction pool
    def add_transaction(self, transaction):
        if validate_transaction(transaction, self.blockchain):
            self.transactionManager.add_transaction(transaction)
            self.lock.acquire()
            print(Fore.YELLOW + f'\rTransaction from {transaction.get_sender_port()} added ' + Style.RESET_ALL)
            self.lock.release()

    # Rozpoczecie wątku wysyłania wiadomości
    def start_transaction_sending_thread(self):
        Thread(target=self.send_transactions).start()

    # Wysyłanie transakcji (w osobnym wątku) do pozostałych nodes
    def send_transactions(self):
        while True:
            # Wysyłanie transakcji w losowej chwili
            random_number = randint(3, 8)
            sleep(random_number)
            if self.transactionManager.get_available_balance() > MIN_FEE:
                transaction = self.transactionManager.generate_transaction()
                if transaction is not None:
                    self.broadcast_transaction(transaction)
                    self.lock.acquire()
                    print(Fore.YELLOW + '\rTransaction sent ' + Style.RESET_ALL)
                    self.lock.release()

    #  Wyświetlenie transakcji
    def print_transactions(self):
        self.transactionManager.print_transactions()

    '''--------------------------------------BLOCKCHAIN---------------------------------------'''

    # Walidacja przychodzącego bloku
    def validate_incoming_block(self, block):
        if validate_block(block):
            is_main_branch_updated = self.blockchain.add(block)
            self.lock.acquire()
            print(Fore.MAGENTA + f'\nNew block from {block.get_winner_port()}' + Style.RESET_ALL)
            print(self.blockchain.get_info())
            self.lock.release()
            # Jeśli main branch się zmienił to kopanie bieżącego bloku powinno zostać przerwane '''
            if self.miner.is_active:
                if is_main_branch_updated:
                    self.stop_mining()
                    self.transactionManager.filter_transactions()
                    self.start_mining()
                else:
                    print(Fore.MAGENTA + f'Mining continued\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Block rejected' + Style.RESET_ALL)

    def get_blockchain_json(self):
        return self.blockchain.get_json()

    def pull_blockchain(self):
        try:
            response = requests.get(url='http://127.0.0.1:5000/blockchain')
            blockchain_dict = response.json()
            self.blockchain.pull(blockchain_dict)
        except:
            'Connection denied'

    # Wyświetlenie blockchain
    def print_blockchain(self):
        self.blockchain.print()

    # Zapisywanie blockchain do pliku
    def save_blockchain(self):
        self.blockchain.save(self.__PORT)

    # TODO
    # Wczytanie blockchain'a z pliku i walidacja
    # @staticmethod
    # def load_and_validate_blockchain():
    #     blockchain = Blockchain.load_from_file()
    #     validate_blockchain(blockchain)

    '''--------------------------------------BROADCASTING---------------------------------------'''

    # Powiadomienie o dodaniu nowego node'a do sieci
    def broadcast_new_node(self, new_public_key, new_ip):
        self.__broadcast('/update-list', get_identity_json(new_public_key, new_ip))
        print(Fore.CYAN + 'Other nodes have been notified' + Style.RESET_ALL)

    # Wysłanie nowego bloku do pozostałych node'ów
    def broadcast_new_block(self, block):
        self.__broadcast('/blockchain', block.to_json())

    # Powiadomienie o transakcji
    def broadcast_transaction(self, transaction):
        self.__broadcast('/transactions', transaction.to_json(), True)
        print(Fore.YELLOW + 'Transaction sent' + Style.RESET_ALL)

    def cheat(self):
        random_block = choice(self.blockchain.main_branch.copy())
        cheated_block = Block(**random_block.to_dict())
        random_transaction = choice(cheated_block.transactions)
        doubled_transaction = Transaction(**random_transaction.to_dict())
        cheated_block.transactions.append(doubled_transaction)
        self.broadcast_new_block(cheated_block)

    '''--------------------------------------MINING---------------------------------------'''

    # Rozpoczęcie kopania w oddzielnym wątku
    def start_mining(self):
        if not self.miner.is_active:
            self.transactionManager.filter_transactions()
            self.miner.is_active = True
        Thread(target=self.mine).start()

    def stop_mining(self):
        self.miner.stop()

    def deactivate_miner(self):
        self.stop_mining()
        self.miner.is_active = False

    # Kopanie nowego bloku i rogłoszenie w razie zwycięstwa
    def mine(self):
        while self.transactionManager.is_transaction_pool_empty():
            sleep(0.1)
        transactions_dict = self.transactionManager.pop_transactions()
        block = self.miner.run(self.blockchain.get_last_header(), transactions_dict)
        if block is not None:
            self.broadcast_new_block(block)
            print(Fore.GREEN + '\nWINNER!' + Style.RESET_ALL)
            self.blockchain.add(block)
            print(self.blockchain.get_info())
            self.transactionManager.filter_transactions()
            self.start_mining()

    def risk(self, mode: bool):
        if self.blockchain.risk_mode != mode:
            self.blockchain.set_risk_mode(mode)
            message = 'Risk mode activated' if mode else 'Risk mode deactivated'
            print(Fore.CYAN + '\n' + message + Style.RESET_ALL)

    '''-----------------------------------COMMUNICATION---------------------------------------'''

    # Wysłanie requestu do innego node'a i zwrócenie odpowiedzi
    @staticmethod
    def __send_request(url, json):
        try:
            response = requests.post(url=url, json=json)
            return response
        except:
            print('Connection denied')

    # Rozgłoszenie danych do pozostałych nodes
    def __broadcast(self, endpoint, json, risk=False):
        for public_key, ip in self.keyManager.get_nodes_items():
            if ip != self.__IP:
                if not risk or random() <= 0.8:
                    self.__send_request(ip + endpoint, json)
