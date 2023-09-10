import logging
import sys
from threading import Thread
from time import sleep

from colorama import init
from flask import Flask, request

from block import Block
from console import Console
from crypto_util import get_dict
from node import Node
from transaction import Transaction

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
init()

node = Node(sys.argv[1])


# Wysyłanie nowy node
@app.post('/new-node')
def add_new_node():
    node_dict = get_dict(request)
    new_public_key = node_dict['public key']  # Nowy klucz publiczny
    new_ip_addr = node_dict['ip']  # Nowy adres IP
    node.add_new_node(new_public_key, new_ip_addr)
    return node.get_nodes_list_json(), 201


# Wysyłanie aktualizacja listy kluczy publicznych
@app.post('/update-list')
def update_list_of_nodes():
    node_dict = get_dict(request)
    new_public_key = node_dict['public key']  # Nowy klucz publiczny
    new_ip_addr = node_dict['ip']  # Nowy adres IP
    node.update_nodes_list(new_public_key, new_ip_addr)
    return '', 200


# Odbieranie transakcji
@app.post('/transactions')
def add_transaction():
    transaction_dict = get_dict(request)
    transaction = Transaction(**transaction_dict)
    node.add_transaction(transaction)
    return '', 200


# Odbieranie bloku od node'a, który wygrał
@app.post('/blockchain')
def add_block():
    block_dict = get_dict(request)
    block = Block(**block_dict)
    node.validate_incoming_block(block)
    return '', 200


# Pobranie blockchaina od danego node'a
@app.get('/blockchain')
def get_blockchain():
    return node.get_blockchain_json(), 200


# Rozpoczęcie pracy serwera
def start_server():
    Console(node).start()
    Thread(target=lambda: app.run(port=int(node.get_port()), debug=False)).start()
    if node.get_port() != '5000':
        node.connect('http://127.0.0.1:5000')
    sleep(10)
    node.start_transaction_sending_thread()
    sleep(5)
    node.start_mining()


if __name__ == '__main__':
    start_server()

