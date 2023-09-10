from threading import Thread
from node import Node


class Console(Thread):

    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.connected = False

    # Tekstowy interfejs użytkownika
    def run(self):
        while True:
            command = input()
            match command:
                case 'connect':
                    self.connect()
                case 'pn':
                    self.node.print_nodes_list()
                case 'b':
                    self.node.check_balance()
                case 't':
                    self.node.start_transaction_sending_thread()
                case 'pt':
                    self.node.print_transactions()
                case 'm':
                    self.node.start_mining()
                case 'dm':
                    self.node.deactivate_miner()
                case 'pb':
                    self.node.print_blockchain()
                case 'sb':
                    self.node.save_blockchain()
                case 'risk':
                    self.node.risk(True)
                case 'unrisk':
                    self.node.risk(False)
                case 'pull':
                    self.node.pull_blockchain()
                case 'cheat':
                    self.node.cheat()
                # case 'load blockchain':
                #     self.node.load_and_validate_blockchain()
                case _:
                    print(f'Command is not recognized')

    def connect(self):
        if self.connected:
            print('Already connected')
        else:
            port_dest = input('Enter destination PORT: ')
            if port_dest != self.node.get_port():
                self.node.connect('http://127.0.0.1:' + port_dest)
            else:
                print('Destination PORT must be different from the own')
