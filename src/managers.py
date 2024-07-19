import json
import random
import string
import base64

from customtkinter import filedialog

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from components import Gui, TopLevelGui
from .config import FILES_TYPE


class FileManager:
    @classmethod
    def get_file_to_save(cls, gui: Gui | TopLevelGui) -> str:
        file_p = filedialog.asksaveasfilename(
            title="Save file", filetypes=FILES_TYPE, defaultextension=FILES_TYPE
        )
        if not file_p:
            return gui.show_messages("Error", "Invalid file")
        return file_p

    @classmethod
    def get_file(cls, gui: Gui | TopLevelGui) -> str:
        file_p = filedialog.askopenfilename(
            title="Load file", filetypes=FILES_TYPE, defaultextension=FILES_TYPE
        )
        if file_p is None:
            return gui.show_messages("Error", "Invalid file")
        return file_p

    @classmethod
    def load_passwords_file(cls, file_p: str, gui: Gui | TopLevelGui):
        gui.values["passwds"] = file_p
        gui.values["passwds_name"] = cls.get_filename(file_p)

    @classmethod
    def save_file(cls, data: bytes, gui: Gui | TopLevelGui) -> None:
        file_p = cls.get_file_to_save(gui)
        with open(file_p, "wb") as f:
            f.write(data)

    @classmethod
    def get_filename(cls, file_p: str) -> str:
        file_s = file_p.split("/")
        name = file_s[len(file_s) - 1]
        return name

    @classmethod
    def get_file_backup(cls, file_p: str) -> str:
        file_name = cls.get_filename(file_p)
        file_name_bak = f"{file_name}.bak"
        path = file_p.split("/")
        path.pop()
        path.append(file_name_bak)
        path_bak = "/".join(path)
        return path_bak

    @classmethod
    def read_storefile(cls, gui: Gui | TopLevelGui) -> bool:
        file_p = gui.values.get("passwds")
        if file_p is None:
            gui.show_messages("Error", "No passwords loaded")
            return False
        with open(file_p, "rb") as f:
            gui.values["passwds_data_enc"] = f.readlines()
        return True

    @classmethod
    def file_lines_count(cls, path: str) -> int:
        count = 0
        with open(path, "rb") as f:
            for _ in f.read():
                count += 1
        return count

    @classmethod
    def overwrite_storefile(
        cls, path: str, data: list[str], gui: Gui
    ):
        # BACKUP FILE
        path_bak = cls.get_file_backup(path)
        f = open(path, "r+")
        file_data = f.read()
        with open(path_bak, "w") as f_bak:
            f_bak.write(file_data)

        # DELETE OLD FILE CONTENT
        f.read()
        f.seek(0)
        f.truncate()
        f.close()

        # OVERWRITE FILE
        new_data = []
        for d in data:
            b64_data = KeyManager.encrypt_message(payload=d, gui=gui)
            new_data.append(b64_data)
        for line in new_data:
            with open(path, "a") as f:
                if cls.file_lines_count(path) == 0:
                    f.write(line)
                else:
                    f.write("\n" + line)

    @classmethod
    def write_storefile(cls, gui: Gui, payload: dict[str, str]) -> None:
        data = KeyManager.encrypt_message(payload=payload, gui=gui)
        file_p = gui.values.get("passwds")
        if data is None:
            return gui.show_messages("Error", "No encrypted data stored")
        if file_p is None:
            file_p = cls.get_file_to_save(gui=gui)
            cls.load_passwords_file(file_p=file_p, gui=gui)

        with open(file_p, "a") as f:
            if cls.file_lines_count(path=file_p) == 0:
                f.write(data)
            else:
                f.write("\n" + data)
        return gui.show_messages("Success", "Data saved")

    @classmethod
    def search_password(cls, service: str, gui: Gui) -> None:
        passwords = gui.values.get("passwds_data_dec")
        passwd_found = None
        for passwd in passwords:
            if service == passwd["service"]:
                passwd_found = passwd
                break
        if passwd_found is None:
            return gui.show_messages(
                "Warning", "There is not a stored password for this service"
            )
        gui.values["passwd_found"] = passwd_found
        text = f"Service: {passwd_found["service"]}\nUsername: {passwd_found["username"]}\nPassword: {passwd_found["password"]}"
        gui.values["passwd_found_box"] = gui.update_textbox_content(
            box=gui.values["passwd_found_box"],
            cnt={"index": "0.0", "text": text},
        )
        return gui.show_messages("Success", "Password found")

    @classmethod
    def update_password(
        cls, gui: Gui, payload: dict[str, str]
    ) -> None:
        index = 0
        old_passwd = gui.values.get("passwd_found")
        file_p: str = gui.values.get("passwds")
        passwords: list[dict] = gui.values.get("passwds_data_dec")
        for passwd in passwords:
            if old_passwd["service"] != passwd["service"]:
                index += 1
                continue
            passwords[index] = payload
        gui.values["passwds_data_dec"] = passwords
        gui.values["passwd_found"] = payload
        cls.overwrite_storefile(path=file_p, data=passwords, gui=gui)
        box_cnt = {
            "index": "0.0",
            "text": f"Service: {payload["service"]}\nUsername: {payload["username"]}\nPassword: {payload["password"]}",
        }
        gui.values["passwd_found_box"] = gui.update_textbox_content(
            box=gui.values["passwd_found_box"], cnt=box_cnt
        )
        return gui.show_messages("Success", "Password successfuly updated")

    @classmethod
    def delete_password(cls, gui: Gui):
        index = 0
        passwd_to_del = gui.values["passwd_found"]
        passwords: list[dict] = gui.values["passwds_data_dec"]
        file_p: str = gui.values["passwds"]
        for passwd in passwords:
            if passwd_to_del != passwd:
                index += 1
                continue
            passwords.pop(index)
            gui.values["passwds_data_dec"] = passwords
        cls.overwrite_storefile(path=file_p, data=passwords, gui=gui)
        box_cnt = {"index": "0.0", "text": ""}
        gui.values["passwd_found_box"] = gui.update_textbox_content(
            box=gui.values["passwd_found_box"], cnt=box_cnt
        )
        del gui.values["passwd_found"]
        return gui.show_messages("Success", "Password successfuly deleted")


class KeyManager:
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
    def pkey_password_match(cls, passwd: str, passwd_match: str, gui: Gui) -> None:
        if passwd != passwd_match:
            return gui.show_messages("Error", "Password mismatch")
        pkey = cls.generate_pkey(passwd)
        FileManager.save_file(pkey, gui)
        return gui.show_messages("Success", "Key created")

    @classmethod
    def get_pkey(cls, file_p: str, passwd: str, gui: Gui) -> None:
        with open(file_p, "rb") as keyfile:
            try:
                pkey = serialization.load_pem_private_key(
                    keyfile.read(), password=passwd.encode()
                )
                gui.values["pkey"] = pkey
                gui.values["pubkey"] = pkey.public_key()
                gui.values["pkey_name"] = FileManager.get_filename(file_p)
            except ValueError as e:
                return gui.show_messages("Error", e)
        gui.show_messages("Check", "Key successfuly loaded")
        gui.values["pkey_lbl"].configure(
            text=f"Current Key:\n{gui.values.get("pkey_name")}"
        )

    @classmethod
    def encrypt_message(
        cls,
        payload: dict[str, str],
        gui: Gui,
    ) -> str | None:
        key: rsa.RSAPublicKey = gui.values.get("pubkey")
        if key is None:
            gui.show_messages("Error", "No key loaded")
            return gui.close_window()
        data = json.dumps(payload).encode()
        encrypted_data = key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        b64_enc_data = base64.b64encode(encrypted_data).decode()
        return b64_enc_data

    @classmethod
    def decrypt_message(cls, gui: Gui | TopLevelGui) -> bool:
        encrypted_data = gui.values.get("passwds_data_enc")
        key: rsa.RSAPrivateKey = gui.values.get("pkey")
        if encrypted_data is None:
            gui.show_messages("Error", "No password data")
            return False
        if key is None:
            gui.show_messages("Error", "No key loaded")
            return False

        decrypted_data = []
        try:
            for data in encrypted_data:
                d_data = key.decrypt(
                    base64.b64decode(data),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                decrypted_data.append(json.loads(d_data))
        except ValueError as e:
            gui.show_messages("Error", e)
            return False
        gui.values["passwds_data_dec"] = decrypted_data
        return True


class PasswordManager:
    @classmethod
    def gen_lowercase(cls, length: int):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

    @classmethod
    def gen_uppercase(cls, length: int):
        return "".join(random.choice(string.ascii_uppercase) for _ in range(length))

    @classmethod
    def gen_digits(cls, length: int):
        return "".join(random.choice(string.digits) for _ in range(length))

    @classmethod
    def gen_special_chars(cls, length: int):
        return "".join(random.choice(string.punctuation) for _ in range(length))

    @classmethod
    def validate_password(cls, password: str):
        for i in range(len(password) - 1):
            if password[i] == password[i + 1]:
                return False
        return True

    @classmethod
    def gen_password(cls, gui: Gui | TopLevelGui, length: int = 24):
        divider = 3

        precise_divider = False
        if length % divider == 0:
            precise_divider = True

        common = length // divider
        special = length - (common * 3)

        if precise_divider:
            common -= 1
            special += divider

        while True:
            chars = (
                cls.gen_lowercase(common)
                + cls.gen_uppercase(common)
                + cls.gen_digits(common)
                + cls.gen_special_chars(special)
            )
            generated_password = "".join(random.sample(chars, length))
            if cls.validate_password(generated_password):
                gui.show_messages("Success", "Password successfully generated")
                return generated_password
