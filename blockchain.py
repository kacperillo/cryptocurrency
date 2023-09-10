import json

from colorama import Fore, Style
from block import Block
from output import Output
from transaction import Transaction

INITIAL_OUTPUTS = [
    Output('0', 'http://127.0.0.1:5000', 1000),
    Output('1', 'http://127.0.0.1:5000', 1000),
    Output('0', 'http://127.0.0.1:5001', 1000),
    Output('1', 'http://127.0.0.1:5001', 1000),
    Output('0', 'http://127.0.0.1:5002', 1000),
    Output('1', 'http://127.0.0.1:5002', 1000),
    Output('0', 'http://127.0.0.1:5003', 1000),
    Output('1', 'http://127.0.0.1:5003', 1000),
    Output('0', 'http://127.0.0.1:5004', 1000),
    Output('1', 'http://127.0.0.1:5004', 1000),
    Output('0', 'http://127.0.0.1:5005', 1000),
    Output('1', 'http://127.0.0.1:5005', 1000),
    Output('0', 'http://127.0.0.1:5006', 1000),
    Output('1', 'http://127.0.0.1:5006', 1000)
]

INITIAL_COINBASE_TRANSACTION = Transaction('0', None, [output.to_dict() for output in INITIAL_OUTPUTS], 0, '', '')
GENESIS_BLOCK = Block('', 0, '0', [INITIAL_COINBASE_TRANSACTION.to_dict()])


class Blockchain:

    def __init__(self):
        self.main_branch = [GENESIS_BLOCK]
        self.branches = [self.main_branch]
        self.orphan_blocks = []
        self.risk_mode = False
        self.risk_branch = None

    # Dołączenie nowego bloku, zwraca True jeśli main branch został zmieniony
    def add(self, new_block):
        is_main_branch_updated = False
        # Szukanie miejsca, do którego może zostać dołączony nowy blok
        branch, is_new_branch_created = self.__find_branch_for_block(new_block)
        if branch is None:
            self.orphan_blocks.append(new_block)
        else:
            if not self.__is_double_spending(branch, new_block):
                branch.append(new_block)
                self.__add_possible_orphan_blocks(new_block, branch)
                if branch == self.main_branch:
                    is_main_branch_updated = True
                elif self.risk_mode:
                    is_main_branch_updated = False
                else:
                    is_main_branch_updated = self.__choose_main_branch()
                if is_new_branch_created:
                    print(Fore.MAGENTA + '\nNew branch created' + Style.RESET_ALL)
            else:
                print(Fore.RED + f'Rejected' + Style.RESET_ALL)
                self.branches.remove(branch) if is_new_branch_created else None
        return is_main_branch_updated

    def __find_branch_for_block(self, new_block):
        is_new_branch_created = False
        for branch in self.branches:
            # Jeśli blok jest ostatnim w gałęzi, to nowy blok zostanie dołączony bez tworzenia nowej gałęzi
            if new_block.previous_header == branch[-1].header:
                return branch, is_new_branch_created
        for branch in self.branches:
            for block in branch:
                if not new_block.previous_header == block.header:
                    continue
                new_branch = self.__create_new_branch(branch, block)
                is_new_branch_created = True
                return new_branch, is_new_branch_created
        return None, is_new_branch_created

    # Stworzenie nowej gałęzi blokchaina
    def __create_new_branch(self, old_branch, last_block_in_old_branch):
        new_branch = []
        for block in old_branch:
            new_branch.append(block)
            if block == last_block_in_old_branch:
                break
        self.branches.append(new_branch)
        return new_branch

    # Sprawdzenie czy nowy block jest rodzicem dla któregoś z orphan bloków
    def __add_possible_orphan_blocks(self, block, branch):
        for orphan in self.orphan_blocks:
            if orphan.__eq__(block):
                self.orphan_blocks.remove(orphan)
                break
            if orphan.previous_header == block.header:
                if not self.__is_double_spending(branch, orphan):
                    self.orphan_blocks.remove(orphan)
                    branch.append(orphan)
                    self.__add_possible_orphan_blocks(orphan, branch)
                    break

    # Wybranie najdłuższej, czyli głównej gałęzi blockchain'a, zwraca True jeśli zmieniła się główna gałąź
    def __choose_main_branch(self):
        is_main_branch_updated = False
        longest_branch = self.main_branch
        for branch in self.branches:
            if len(branch) > len(longest_branch):
                longest_branch = branch
        if longest_branch != self.main_branch:
            self.main_branch = longest_branch
            is_main_branch_updated = True
            print(Fore.MAGENTA + '\nMain branch switched' + Style.RESET_ALL)
        return is_main_branch_updated

    # Zwrócenie header'a ostatniego bloku głównej gałęzi
    def get_last_header(self):
        return self.main_branch[-1].header

    # Zwrócenie wszystkich transakcji z gałęzi
    @staticmethod
    def get_all_transactions(branch):
        return [transaction for block in branch for transaction in block.transactions]

    # Zwrócenie wszystkich inputów, czyli wydanych outputów należących do węzła o danym ip
    def __filter_inputs(self, ip, branch):
        return [transaction.input for transaction in self.get_all_transactions(branch)
                if transaction.input is not None and transaction.input.owner_ip == ip]

    # Zwrócenie wszystkich outputów należących do węzła o danym ip
    def __filter_outputs(self, ip, branch):
        return [output for transaction in self.get_all_transactions(branch)
                for output in transaction.outputs
                if output.owner_ip == ip]

    # Zwrócenie wszystkich niewydanych outputów (z danej gałęzi)
    def get_unspent_outputs(self, ip, branch):
        inputs = self.__filter_inputs(ip, branch)
        outputs = self.__filter_outputs(ip, branch)
        return [output for output in outputs if output not in inputs]

    def __is_double_spending(self, branch, block):
        for transaction in block.transactions:
            input = transaction.input
            if input is None:
                continue
            if not self.__is_input_unspent(input, branch):
                return True
        return False

    def __is_input_unspent(self, input, branch):
        sender_ip = input.owner_ip
        unspent_outputs = self.get_unspent_outputs(sender_ip, branch)
        for unspent_output in unspent_outputs:
            if input.__eq__(unspent_output):
                return True
        print(f'From {input.get_owner_port()}: Input does not exist or is already spent')
        return False

    def get_main_and_outside_transactions(self):
        main_branch_transactions = self.get_all_transactions(self.main_branch)
        outside_transactions = []
        branches = self.branches.copy()
        branches.append(self.orphan_blocks.copy())
        for branch in branches:
            if branch == self.main_branch:
                continue
            for block in branch:
                for block_transaction in block.transactions:
                    if block_transaction.is_in_list(main_branch_transactions) or \
                            block_transaction.is_in_list(outside_transactions) or \
                            block_transaction.is_coinbase():
                        continue
                    if self.__is_input_unspent(block_transaction.input, self.main_branch):
                        outside_transactions.append(block_transaction)
        return main_branch_transactions, outside_transactions

    # Wyświetlenie blockchain'a w konsoli
    def print(self):
        print(json.dumps([(block.to_dict()) for block in self.main_branch], indent=4))

    # Zapisanie blockchain'a w pliku
    def save(self, port):
        path = 'blockchain/blockchain' + port + '.json'
        blocks_dict = [(block.to_dict()) for block in self.main_branch]
        with open(path, 'w') as file:
            json.dump(blocks_dict, file, indent=4)

    def get_info(self):
        return f'\tMain branch: {len(self.main_branch)} blocks\n' \
               f'\tBranches: {len(self.branches)}\n' \
               f'\tOrphan blocks: {len(self.orphan_blocks)}'

    # Utworzenie pustego blockchaina
    @staticmethod
    def empty():
        blockchain = Blockchain()
        blockchain.main_branch = []
        return blockchain

    # Utworzenie blockchaina na podstawie wczytanego pliku
    @staticmethod
    def load_from_file():
        blockchain = Blockchain.empty()
        with open('blockchain/test_blockchain.json', 'r') as file:
            try:
                blocks_dict = json.load(file)
                for block_dict in blocks_dict:
                    blockchain.add(Block(**block_dict))
                return blockchain
            except:
                print('Blockchain structure incorrect')
                return None

    def set_risk_mode(self, mode):
        self.risk_mode = mode
        if mode:
            self.risk_branch = self.__create_new_branch(self.main_branch, self.main_branch[-1])
            self.main_branch = self.risk_branch
            print(Fore.MAGENTA + '\nMain branch switched' + Style.RESET_ALL)
        else:
            self.__choose_main_branch()

    def get_json(self):
        blockchain_dict = [[block.to_dict() for block in branch] for branch in self.branches]
        return json.dumps(blockchain_dict, indent=4)

    def pull(self, blockchain_dict):
        for branch_dict in blockchain_dict:
            branch = [Block(**block_dict) for block_dict in branch_dict]
            self.branches.append(branch)
        self.remove_dubled_orphan_blocks()
        self.__choose_main_branch()
        print(self.get_info())

    def remove_dubled_orphan_blocks(self):
        for branch in self.branches:
            for block in branch:
                if self.orphan_blocks is None:
                    return
                for orphan in self.orphan_blocks:
                    if orphan.__eq__(block):
                        self.orphan_blocks.remove(orphan)
                        break
