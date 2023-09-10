from ecdsa.keys import VerifyingKey, BadSignatureError
from crypto_util import calculate_fee, TARGET, REWARD


def validate_header(block):
    if not block.__hash__() == block.header:
        print('Header of block has been changed')
        return False
    if not (int(block.header, 16) < TARGET):
        print('Hash of block is invalid')
        return False
    return True


def validate_money(transaction):
    if transaction.input.amount != (transaction.get_outputs_amount() + transaction.fee):
        print('Input is not equal to sum of outputs')
        return False
    required_fee = sum([calculate_fee(output.amount) for output in transaction.outputs
                        if output.owner_ip != transaction.input.owner_ip])
    if transaction.fee != required_fee:
        print('Transaction fee is invalid')
        return False
    return True


def validate_signature(transaction):
    signature = transaction.signature
    public_key = transaction.public_key
    try:
        public_key = VerifyingKey.from_string(bytearray.fromhex(public_key))
        signature = bytearray.fromhex(signature)
        public_key.verify(signature, transaction.__hash__().encode('utf-8'))
        return True
    except BadSignatureError:
        print('Signature is invalid (transaction has been changed)')
        return False
    except ValueError:
        print('Signature is invalid (non-heaxadecimal number)')
    except:
        print('Signature is invalid (public has been changed key)')


def validate_coinbase_transaction(total_fee, coinbase_transaction):
    if coinbase_transaction is None:
        print('Coinbase transaction does not exist')
        return False
    if coinbase_transaction.get_outputs_amount() != total_fee + REWARD:
        print('Coinbasee transaction amount is invalid')
        return False
    return True


def validate_block(block):
    used_inputs = []
    total_fee = 0
    coinbase_transaction = None
    # Wszystkie transakcje wysyłki
    for transaction in block.transactions:
        input = transaction.input
        # tylko jedno coinbase transaction
        if input is None:
            if coinbase_transaction is not None:
                print('More than one coinbase transaction')
                return False
            coinbase_transaction = transaction
            continue
        if input in used_inputs:
            print('Input is duplicated')
            return False
        if not validate_money(transaction) or not validate_signature(transaction):
            return False
        total_fee += transaction.fee
        used_inputs.append(input)
    if not validate_coinbase_transaction(total_fee, coinbase_transaction):
        return False
    if not validate_header(block):
        return False
    return True


def validate_transaction(transaction, blockchain):
    return validate_input(transaction.input, blockchain) and \
           validate_money(transaction) and \
           validate_signature(transaction)


def validate_input(input, blockchain):
    sender_ip, id = input.owner_ip, input.transaction_id
    unspent_outputs = blockchain.get_unspent_outputs(sender_ip, blockchain.main_branch)
    for unspent_output in unspent_outputs:
        if input.__eq__(unspent_output):
            return True
    print(f'From {input.get_owner_port()}: Input does not exist or is already spent')
    return False

# # Wczytanie blockchain'a z pliku i walidacja
# def validate_blockchain(blockchain):
#     if blockchain is None:
#         print('Blockchain is empty')
#         return False
#     blockchain_validated = Blockchain.empty()
#     for i, block in enumerate(blockchain.blocks):
#         if i == 0 and block.header == GENESIS_BLOCK.header:
#             print('Genesis block')
#             blockchain_validated.add(block)
#             continue
#         if not validate_block(block, blockchain_validated):
#             print(f'Cheating in {i} block')
#             print('Blockchain is not valid')
#             return False
#         print(f'Hash {i} is valid')
#         blockchain_validated.add(block)
#     print('Blockchain is valid')
#     return True

