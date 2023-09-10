import hashlib
import json
from secrets import token_bytes
from Crypto.Cipher import AES
from ecdsa.keys import SigningKey

# Parametry procesu kopania i walidacji
MAX_NONCE = 2 ** 32  # 4 billion
DIFFICULTY_BITS = 20
TARGET = 2 ** (256 - DIFFICULTY_BITS)
MAX_BLOCK_TRANSACTIONS = 5
MIN_FEE = 1
TAX = 0.1
REWARD = 10


def define_port():
    while True:
        #  Wpisanie portu z konsoli
        port = input('Enter PORT number (5000 - 6000): ')
        try:
            # Obsługa błędu - numer z poza zakresu
            if int(port) < 5000 or int(port) > 6000:
                print('Invalid number\n')
            else:
                # Przypisanie podanego numeru
                return port
        except ValueError:
            # Obsługa błędu - użytkownik nie podał numeru
            print('PORT must be a number\n')


# Utworzenie wirtualnej tożsamości
def create_keys(password_path, privkey_path):
    private_key = SigningKey.generate()  # Klucz prywatny
    public_key = private_key.verifying_key  # Klucz publiczny
    # Wygenerowanie i zapisanie do pliku klucza do zaszyfrowania klucza prywatnego
    key = token_bytes(16)  # Klucz
    file = open(password_path, 'wb')
    file.write(key)
    file.close()
    nonce, ciphertext, tag = encrypt(private_key.to_string(), key, True)
    crypto_dict = {
        'nonce': nonce.hex(),
        'ciphertext': ciphertext.hex(),
        'tag': tag.hex()
    }
    json_object = json.dumps(crypto_dict)
    with open(privkey_path, 'w') as f:
        f.write(json_object)
    return public_key.to_string().hex()


# Funkcja szyfrująca
def encrypt(msg, key, if_key):
    # Zdefiniowanie szyfru
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    if if_key:
        ciphertext, tag = cipher.encrypt_and_digest(msg)
    else:
        ciphertext, tag = cipher.encrypt_and_digest(msg.encode('utf-8'))
    return nonce, ciphertext, tag


# Funkcja odszyfrowująca
def decrypt(nonce, ciphertext, tag, key, if_key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        if if_key:
            return plaintext
        else:
            return plaintext.decode('utf-8')
    except:
        return False


def compute_hash(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()


def __compute_hash(last_header, nonce, transactions_dict):
    return hashlib.sha256(last_header.encode('utf-8')
                          + str(nonce).encode('utf-8')
                          + str(transactions_dict).encode('utf-8')).hexdigest()


def proof_of_work(last_header, transactions_dict, stop_event):
    for nonce in range(MAX_NONCE):
        hash_result = __compute_hash(last_header, nonce, transactions_dict)
        # print(hash_result)
        if (int(hash_result, 16) < TARGET) and (not stop_event.is_set()):
            return hash_result, nonce
        if stop_event.is_set():
            return None, None


def calculate_fee(amount):
    return round(amount * TAX) if round(amount * TAX) >= MIN_FEE else MIN_FEE


def get_identity_json(public_key, ip):
    return json.dumps({'public key': public_key, 'ip': ip})


def get_dict(request):
    return json.loads(request.get_json())
