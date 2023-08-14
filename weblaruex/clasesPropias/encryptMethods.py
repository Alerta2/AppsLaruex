from cryptography.fernet import Fernet
import base64
from datetime import datetime
import pytz


def write_key(nombre):
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open(nombre+".key", "wb") as key_file:
        key_file.write(key)

def load_key(nombre):
    """
    Loads the key from the current directory named `key.key`
    """
    return open(nombre+".key", "rb").read()

def encryptText(text, key):
    """
    It takes a file, encrypts it, and saves it as a new file.
    
    :param text: The text to be encrypted
    :param key: The key used to encrypt the file
    """
    f = Fernet(key)
    return f.encrypt(bytes(text, encoding='utf8'))

def decryptText(text, key):
    """
    It takes the encrypted file and decrypts it using the key
    
    :param text: The name of the file you want to encrypt or decrypt
    :param key: The key used to encrypt the file, or an instance of Fernet
    """
    f = Fernet(key)
    return f.decrypt(text)


def encryptFile(filename, key):
    """
    Given a filename (str) and key (bytes), it encrypts the file and write it
    """
    f = Fernet(key)

    with open(filename, "rb") as file:
            # read all file data
            file_data = file.read()

            # encrypt data
            encrypted_data = f.encrypt(file_data)
            # write the encrypted file
            with open("encryptedFile.ef", "wb") as file:
                file.write(encrypted_data)

def decryptFile(filename, key):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    f = Fernet(key)
    with open("encryptedFile.ef", "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)

    # write the original file
    with open(filename, "wb") as file:
        file.write(decrypted_data)

def stringToDatetime(fechaString):
    """
    Given a string with the format 'YYYY-MM-DD', it returns a datetime object
    """
    fechaString = fechaString.replace("-00:15", "")
    return datetime.strptime(fechaString, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone("Europe/Madrid"))

def bytesToString(bytes):
    """
    Given a bytes object, it returns a string
    """
    return bytes.decode('utf-8')

def stringToBytes(string):
    """
    Given a string, it returns a bytes object
    """
    return bytes(string, 'utf-8')