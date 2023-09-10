import json
from random import choice
from ecdsa.keys import SigningKey
from crypto_util import create_keys, decrypt, get_identity_json


class KeyManager:

    def __init__(self, ip, port):
        self.__IP = ip
        self.__PASSWORD_PATH = 'private/password' + port + '.txt'  # Nazwa pliku do zapisu hasła do zaszyfrowania klucza
        self.__PRIVKEY_PATH = 'private/privkey' + port + '.json'  # Nazwa pliku do zapisu zaszyfrowanego klucza
        self.__public_key = create_keys(self.__PASSWORD_PATH, self.__PRIVKEY_PATH)
        self.nodes = {self.__public_key: self.__IP}  # Lista połączonych nodów

    def get_my_ip(self):
        return self.__IP

    def get_my_public_key(self):
        return self.__public_key

    def add_node(self, new_public_key, new_ip_addr):
        self.nodes[new_public_key] = new_ip_addr

    def set_nodes(self, nodes_dict):
        self.nodes = nodes_dict

    def get_nodes_json(self):
        return json.dumps(self.nodes, indent=4)

    def get_nodes_items(self):
        return self.nodes.items()

    def get_my_identity_json(self):
        return get_identity_json(self.__public_key, self.__IP)

    def choose_node(self):
        nodes_ip = list(self.nodes.values())
        nodes_ip.remove(self.__IP)
        return choice(nodes_ip)

    def sign(self, transaction):
        # Import zaszyfrowanego klucza
        f = open(self.__PRIVKEY_PATH)
        data = json.load(f)
        nonce = bytearray.fromhex(data['nonce'])
        ciphertext = bytearray.fromhex(data['ciphertext'])
        tag = bytearray.fromhex(data['tag'])
        # Import hasła
        f1 = open(self.__PASSWORD_PATH, 'rb')
        key = f1.read()
        f1.close()
        # Odszyfrowanie
        pk_decrypted = decrypt(nonce, ciphertext, tag, key, True)
        pk = SigningKey.from_string(pk_decrypted)
        # Podpisanie
        signature = pk.sign(transaction.__hash__().encode('utf-8')).hex()
        transaction.set_signature(signature)
