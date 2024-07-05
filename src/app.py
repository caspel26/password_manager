from typing import Optional

import customtkinter as ctk

from . import config as cfg
from .gui import Gui, TopLevelGui
from .serialize import Key, File


class App:
    def __init__(self) -> None:
        self.window = Gui(title="Password Manager", resizable=(False, False))

        # TABS
        self.tabs = self.window.create_tabs(
            {"width": 700, "height": 500}, ["Keys Manager", "Passwords Manager"]
        )
        KEYS_MANAGER_TAB = self.tabs.tab("Keys Manager")
        PASSWDS_MANAGER_TAB = self.tabs.tab("Passwords Manager")

        # GUI INFO LABELS
        self.lbl_pkey = self.window.create_label(
            txt=f"Key: {self.window.values.get("pkey_name")}",
            pos_data={"relx": 0.061, "rely": 0.90, "anchor": "center"},
        )
        self.lbl_passwd = self.window.create_label(
            txt=f"Passwords: {self.window.values.get("passwds_name")}",
            pos_data={"relx": 0.09, "rely": 0.95, "anchor": "center"},
        )
        self.window.create_label(
            txt=f"Version: {cfg.VERSION}",
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
        )

        # KEYS MANAGER BUTTONS
        self.window.create_button(
            master=KEYS_MANAGER_TAB,
            txt="Generate Key",
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
            cmd=lambda: self.window.open_toplevel_window(EnrollKey(self.window).window),
        )
        self.window.create_button(
            master=KEYS_MANAGER_TAB,
            txt="Load Key",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=self.load_key,
        )

        # PASSWORDS MANAGER BUTTONS
        self.window.create_button(
            master=PASSWDS_MANAGER_TAB,
            txt="Load Passwords",
            pos_data={"relx": 0.5, "rely": 0.1, "anchor": "center"},
            cmd=self.load_passwords,
        )
        self.window.create_button(
            master=PASSWDS_MANAGER_TAB,
            txt="Save Password",
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
            cmd=self.store_password,
        )
        self.search_btn = self.window.create_button(
            master=PASSWDS_MANAGER_TAB,
            txt="Search Password",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=self.search_password,
            state="disabled",
        )

    def load_key(self) -> None:
        self.window.values["key_file"] = ctk.filedialog.askopenfilename(
            title="Select Key File",
            filetypes=cfg.FILES_TYPE,
            defaultextension=cfg.FILES_TYPE,
        )
        if not self.window.values.get("key_file"):
            return self.window.show_messages("Error", "Invalid file")
        gui = LoadKey(self.window)
        self.window.open_toplevel_window(gui.window)
        lbl_cnt = {"text": f"Key: {self.window.values.get("pkey_name")}"}
        self.window.update_label_content(lbl=self.lbl_pkey, cnt=lbl_cnt)
        if self.window.values.get("passwds"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )

    def load_passwords(self) -> None:
        file_p = File.get_file(gui=self.window)
        if not file_p:
            return None
        File.load_passwords_file(file_p=file_p, gui=self.window)
        lbl_cnt = {"text": f"Passwords: {self.window.values.get("passwds_name")}"}
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)
        if self.window.values.get("pkey"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )

    def store_password(self) -> None:
        gui = StoreService(self.window, "Save Password")
        self.window.open_toplevel_window(gui.window)
        lbl_cnt = {"text": f"Passwords: {self.window.values.get("passwds_name")}"}
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)
        if self.window.values.get("pkey") and self.window.values.get("passwds"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )

    def search_password(self) -> None:
        read_success = File.read_storefile(self.window)
        if not read_success:
            return None
        dec_success = Key.decrypt_message(self.window)
        if not dec_success:
            return None
        gui = SearchService(self.window)
        self.window.open_toplevel_window(gui.window)


class EnrollKey:
    def __init__(self, master: Gui) -> None:
        self.window = TopLevelGui(
            master=master, title="Generate Private Key", resizable=(False, False)
        )
        self.window.create_label(
            txt="Enter Password",
            pos_data={"relx": 0.3, "rely": 0.2, "anchor": "center"},
        )
        self.window.create_label(
            txt="Confirm Password",
            pos_data={"relx": 0.7, "rely": 0.2, "anchor": "center"},
        )
        passwd = self.window.create_entry(
            pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"},
            show_text="*"
        )
        match = self.window.create_entry(
            pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"},
            show_text="*"
        )
        self.window.create_button(
            txt="Confirm",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=lambda: Key.pkey_password_match(
                passwd=passwd.get(), passwd_match=match.get(), gui=self.window
            ),
        )
        self.window.create_button(
            txt="Exit",
            pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
            cmd=self.window.close_window,
        )


class LoadKey:
    def __init__(self, master: Gui) -> None:
        self.window = TopLevelGui(
            master=master, title="Load Private Key", resizable=(False, False)
        )
        self.window.create_label(
            txt="Enter Password",
            pos_data={"relx": 0.1, "rely": 0.3, "anchor": "center"},
        )
        self.passwd = self.window.create_entry(
            pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"},
            show_text="*"
        )
        self.window.create_button(
            txt="Confirm",
            pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"},
            cmd=lambda: Key.get_pkey(
                file_p=self.window.master.values.get("key_file"),
                passwd=self.passwd.get(),
                r_gui=self.window.master,
                gui=self.window,
            ),
        )
        self.window.create_button(
            txt="Exit",
            pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
            cmd=self.window.close_window,
        )
        self.window.lock_main_window()


class AddService:
    def __init__(self, master: Gui, title: str) -> None:
        self.window = TopLevelGui(master=master, title=title, resizable=(False, False))
        self.window.create_label(
            txt="Enter Service", pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"}
        )
        self.window.create_label(
            txt="Enter Username",
            pos_data={"relx": 0.5, "rely": 0.2, "anchor": "center"},
        )
        self.window.create_label(
            txt="Enter Password",
            pos_data={"relx": 0.8, "rely": 0.2, "anchor": "center"},
        )
        self.service = self.window.create_entry(
            pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"}
        )
        self.username = self.window.create_entry(
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"}
        )
        self.passwd = self.window.create_entry(
            pos_data={"relx": 0.8, "rely": 0.3, "anchor": "center"},
            show_text="*"
        )
        self.window.create_button(
            txt="Exit",
            pos_data={"relx": 0.8, "rely": 0.7, "anchor": "center"},
            cmd=self.window.close_window,
        )


class StoreService(AddService):
    def __init__(self, master: Gui, title: str) -> None:
        super().__init__(master, title)

        self.window.create_button(
            txt="Save & Encrypt",
            pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
            cmd=lambda: File.write_storefile(
                gui=self.window,
                r_gui=self.window.master,
                payload={
                    "service": self.service.get(),
                    "username": self.username.get(),
                    "password": self.passwd.get(),
                },
            ),
        )
        self.window.lock_main_window()


class UpdateService(AddService):
    def __init__(self, master: Gui, title: str) -> None:
        super().__init__(master, title)

        self.window.create_button(
            txt="Update & Encrypt",
            pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
            cmd=lambda: File.update_password(
                r_gui=self.window.master.master,
                gui=self.window,
                main_gui=self.window.master,
                payload={
                    "service": self.service.get(),
                    "username": self.username.get(),
                    "password": self.passwd.get(),
                },
            ),
        )
        self.window.lock_main_window()


class SearchService:
    def __init__(self, master: Gui) -> None:
        self.window = TopLevelGui(
            master=master, title="Search Password", resizable=(False, False)
        )
        self.window.create_label(
            txt="Enter Service", pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"}
        )
        self.service = self.window.create_entry(
            pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"}
        )
        self.window.create_button(
            txt="Search",
            pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
            cmd=self.search_password,
        )
        self.updated_passwd_btn = self.window.create_button(
            txt="Update Password",
            pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
            cmd=self.update_password,
            state="disabled",
        )
        self.delete_passwd_btn = self.window.create_button(
            txt="Delete Password",
            pos_data={"relx": 0.8, "rely": 0.7, "anchor": "center"},
            cmd=self.delete_password,
            state="disabled",
        )
        self.window.create_button(
            txt="Exit",
            pos_data={"relx": 0.5, "rely": 0.9, "anchor": "center"},
            cmd=self.window.destroy,
        )
        self.passwd_found_box: Optional[ctk.CTkTextbox] = None
        self.window.lock_main_window()

    def search_password(self) -> None:
        File.search_password(
            service=self.service.get(), r_gui=self.window.master, gui=self.window
        )
        passwd_found = self.window.values.get("passwd_found")
        if passwd_found is None:
            return None
        text = f"Service: {passwd_found["service"]}\nUsername: {passwd_found["username"]}\nPassword: {passwd_found["password"]}"
        self.passwd_found_box = self.window.create_textbox(
            pos_data={"relx": 0.8, "rely": 0.4, "anchor": "center"},
            data={"index": "0.0", "text": text},
        )
        self.window.update_button_content(
            btn=self.updated_passwd_btn, cnt={"state": "normal"}
        )
        self.window.update_button_content(
            btn=self.delete_passwd_btn, cnt={"state": "normal"}
        )

    def update_password(self) -> None:
        gui = UpdateService(self.window, "Update Password")
        self.window.open_toplevel_window(gui.window)
        passwd_found = self.window.values.get("passwd_found")
        box_cnt = {
            "index": "0.0",
            "text": f"Service: {passwd_found["service"]}\nUsername: {passwd_found["username"]}\nPassword: {passwd_found["password"]}",
        }
        self.window.update_textbox_content(box=self.passwd_found_box, cnt=box_cnt)

    def delete_password(self) -> None:
        File.delete_password(r_gui=self.window.master, gui=self.window)
        box_cnt = {"index": "0.0", "text": ""}
        self.window.update_textbox_content(box=self.passwd_found_box, cnt=box_cnt)
        del self.window.values["passwd_found"]
