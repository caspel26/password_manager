import json
import time
import base64
from pathlib import Path
from typing import Literal
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

BASE_DIR = Path(__file__).resolve().parent.parent
KEY_DIR = Path("keys/")
PASSWD_FILE = Path("passwd.txt")


class File:
    def __init__(self) -> None:
        self.keydir_path =  BASE_DIR / KEY_DIR
        self.passwd_path = BASE_DIR / PASSWD_FILE

    @classmethod
    def check_filepath(cls, path: Path, file_name: str) -> Path:
        filepath = path / file_name
        if filepath.exists():
            choice = input(
                "File with this name already exist. Would you overwrite it? y/n\n"
            ).upper()
            match choice:
                case "Y":
                    return filepath

                case "N":
                    new_file = input("Enter file name:\n")
                    while new_file == file_name:
                        time.sleep(0.3)
                        new_file = input("Please enter a different file name:\n")
                    filepath = path / new_file
                    return filepath

                case _:
                    print("Invalid choice, exit...")
                    time.sleep(0.5)
                    exit()
        return filepath

    def save_keyfile(self, file: str, pkey_cnt: bytes) -> None:
        path = self.keydir_path
        path.mkdir(parents=True, exist_ok=True)
        pkey_filepath = self.check_filepath(path, file)
        with pkey_filepath.open("wb") as f:
            f.write(pkey_cnt)

    def read_storefile(self) -> list[bytes]:
        path = self.passwd_path
        if not path.exists():
            print("You have no stored passwords")
            print("Exit..")
            time.sleep(0.5)
            exit()
        with path.open("rb") as f:
            data = f.readlines()
        return data

    def file_lines_count(self) -> int:
        count = 0
        path = self.passwd_path
        with path.open("rb") as f:
            for _ in f.read():
                count += 1
        return count

    def write_storefile(self, data: str) -> None:
        path = self.passwd_path
        if not path.exists():
            path.touch()
        with path.open("a") as f:
            if not self.file_lines_count():
                f.write(data)
            else:
                f.write("\n" + data)

    def check_key_file(self, file: str) -> Path:
        keypath = self.keydir_path / file
        while not keypath.exists():
            print("Key does not exist.")
            choice = input("Would yout enter a different key? y/n\n").upper()
            match choice:
                case "Y":
                    file = input("Enter key file name: ")
                    keypath = self.keydir_path / file
                case "N":
                    print("Exit...")
                    exit()
        return keypath

    def update_password_file(
        self, passwords: list[dict[str, str]], pubkey: rsa.RSAPublicKey
    ) -> None:
        path = self.passwd_path
        path.unlink()
        for password in passwords:
            payload = {
                "service": password["service"],
                "username": password["username"],
                "password": password["password"],
            }
            data = json.dumps(payload).encode()
            encrypted_data = pubkey.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            b64_encrypted_data = base64.b64encode(encrypted_data).decode()
            self.write_storefile(b64_encrypted_data)


class Key:
    @classmethod
    def generate_pkey(cls, passwd: str) -> bytes:
        pkey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        priv_pem = pkey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passwd.encode()),
        )
        return priv_pem

    @classmethod
    def pkey_password_match(
        cls, passwd: str, passwd_to_match: str
    ) -> tuple[Literal[False], str] | tuple[str, None]:
        MAX_COUNT = 3
        retry_count = 0
        while retry_count <= MAX_COUNT:
            if passwd != passwd_to_match:
                retry_count += 1
                if retry_count == MAX_COUNT:
                    return False, "Max try reached. Exit..."
                print(
                    f"Passwords don't match please try again.\nYou can try : {MAX_COUNT-retry_count} more times"
                )
                passwd = getpass("Enter password for your key: \n")
                passwd_to_match = getpass("Enter it again to confirm: \n")
            else:
                break
        return passwd, None

    @classmethod
    def load_key(cls, file: str, passwd: str) -> rsa.RSAPrivateKey:
        filepath = File().check_key_file(file)
        with filepath.open("rb") as keyfile:
            try:
                pkey = serialization.load_pem_private_key(
                    keyfile.read(), password=passwd.encode()
                )
            except ValueError as e:
                print(e)
                time.sleep(0.3)
                print("Exit...")
                time.sleep(0.5)
                exit()
        return pkey

    @classmethod
    def encrypt_message(
        cls, service: str, username: str, password: str, key: rsa.RSAPublicKey
    ) -> str:
        payload = {
            "service": service,
            "username": username,
            "password": password,
        }
        data = json.dumps(payload).encode()
        encrypted_data = key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        b64_encrypted_data = base64.b64encode(encrypted_data).decode()
        return b64_encrypted_data

    @classmethod
    def decrypt_message(
        cls, encrypted_data: list[bytes], key: rsa.RSAPrivateKey
    ) -> list[dict[str, str]]:
        decrypted_data = []
        try:
            for data in encrypted_data:
                data = key.decrypt(
                    base64.b64decode(data),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                decrypted_data.append(json.loads(data))
        except ValueError as e:
            print(e)
            time.sleep(0.5)
            exit()
        return decrypted_data
