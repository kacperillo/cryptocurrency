from threading import Event

from colorama import Fore, Style

from block import Block
from crypto_util import proof_of_work


class Miner:

    def __init__(self):
        self.is_active = False
        self.stop_mine_event = Event()  # Event, który przerywa kopanie

    # Kopanie
    def run(self, last_header, transactions_dict):
        self.stop_mine_event = Event()
        print(Fore.CYAN + '\nMining started\n' + Style.RESET_ALL)
        hash_result, nonce = proof_of_work(last_header, transactions_dict, self.stop_mine_event)
        if hash_result is not None and nonce is not None:
            return Block(last_header, nonce, hash_result, transactions_dict)
        return None

    # Zatrzymanie kopania
    def stop(self):
        self.stop_mine_event.set()
        print(Fore.LIGHTRED_EX + 'Mining stopped\n' + Style.RESET_ALL)


