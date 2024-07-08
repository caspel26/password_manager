import json
import base64

from customtkinter import filedialog

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from components.gui import Gui, TopLevelGui
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
        if not file_p:
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
        cls, path: str, data: list[str], gui: TopLevelGui, r_gui: Gui
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
            b64_data = KeyManager.encrypt_message(payload=d, gui=gui, r_gui=r_gui)
            new_data.append(b64_data)
        for line in new_data:
            with open(path, "a") as f:
                if cls.file_lines_count(path) == 0:
                    f.write(line)
                else:
                    f.write("\n" + line)

    @classmethod
    def write_storefile(
        cls, gui: TopLevelGui, r_gui: Gui, payload: dict[str, str]
    ) -> None:
        data = KeyManager.encrypt_message(payload=payload, gui=gui, r_gui=r_gui)
        file_p = r_gui.values.get("passwds")
        if data is None:
            return gui.show_messages("Error", "No encrypted data stored")
        if file_p is None:
            file_p = cls.get_file_to_save(gui=gui)
            cls.load_passwords_file(file_p=file_p, gui=r_gui)

        with open(file_p, "a") as f:
            if cls.file_lines_count(path=file_p) == 0:
                f.write(data)
            else:
                f.write("\n" + data)
        return gui.show_messages("Info", "Data saved")

    @classmethod
    def search_password(cls, service: str, r_gui: Gui, gui: TopLevelGui) -> None:
        passwords = r_gui.values.get("passwds_data_dec")
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
        return gui.show_messages("Info", "Password found")

    @classmethod
    def update_password(
        cls, r_gui: Gui, gui: TopLevelGui, main_gui: Gui, payload: dict[str, str]
    ) -> None:
        index = 0
        old_passwd = main_gui.values.get("passwd_found")
        file_p: str = r_gui.values.get("passwds")
        passwords: list[dict] = r_gui.values.get("passwds_data_dec")
        for passwd in passwords:
            if old_passwd["service"] != passwd["service"]:
                index += 1
                continue
            passwords[index] = payload
        r_gui.values["passwds_data_dec"] = passwords
        main_gui.values["passwd_found"] = payload
        cls.overwrite_storefile(path=file_p, data=passwords, gui=gui, r_gui=r_gui)
        gui.show_messages("Info", "Password successfuly updated")
        return gui.close_window()

    @classmethod
    def delete_password(cls, r_gui: Gui, gui: TopLevelGui):
        index = 0
        passwd_to_del = gui.values["passwd_found"]
        passwords: list[dict] = r_gui.values["passwds_data_dec"]
        file_p: str = r_gui.values["passwds"]
        for passwd in passwords:
            if passwd_to_del != passwd:
                index += 1
                continue
            passwords.pop(index)
            r_gui.values["passwds_data_dec"] = passwords
        cls.overwrite_storefile(path=file_p, data=passwords, gui=gui, r_gui=r_gui)
        return gui.show_messages("Info", "Password successfuly deleted")


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
    def pkey_password_match(
        cls, passwd: str, passwd_match: str, gui: TopLevelGui
    ) -> None:
        if passwd != passwd_match:
            return gui.show_messages("Error", "Password mismatch")
        pkey = cls.generate_pkey(passwd)
        FileManager.save_file(pkey, gui)
        gui.show_messages("Info", "Key created")
        return gui.close_window()

    @classmethod
    def get_pkey(cls, file_p: str, passwd: str, r_gui: Gui, gui: TopLevelGui) -> None:
        with open(file_p, "rb") as keyfile:
            try:
                pkey = serialization.load_pem_private_key(
                    keyfile.read(), password=passwd.encode()
                )
                r_gui.values["pkey"] = pkey
                r_gui.values["pubkey"] = pkey.public_key()
                r_gui.values["pkey_name"] = FileManager.get_filename(file_p)
            except ValueError as e:
                return gui.show_messages("Error", e)
        r_gui.show_messages("Check", "Key successfuly loaded")
        return gui.close_window()

    @classmethod
    def encrypt_message(
        cls,
        payload: dict[str, str],
        gui: TopLevelGui,
        r_gui: Gui,
    ) -> str | None:
        key: rsa.RSAPublicKey = r_gui.values.get("pubkey")
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
