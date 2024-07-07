import webbrowser
from typing import Optional

import customtkinter as ctk

from . import config as cfg
from . import KeyManager, FileManager
from components import Gui, TopLevelGui, AnimatedNavbar


class App:
    def __init__(self) -> None:
        self.window = Gui(title="Password Manager", resizable=(False, False))
        self.navbar = Navbar(self.window)


class Navbar:
    def __init__(self, master: Gui) -> None:
        self.window = master

        self.navbar_frame = AnimatedNavbar(
            master=self.window,
            pos_data={"relx": 0, "relheight": 1, "relwidth": 0.08},
            min_width=0.08,
            max_width=0.3,
        )

        # NAVBAR LABELS
        self.home_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": -0.03, "rely": 0.2},
        )
        self.keys_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": -0.03, "rely": 0.3},
        )
        self.passwds_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": 0, "rely": 0.4},
        )

        # NAVBAR BUTTONS
        self.navbar_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("navbar.png", (25, 25)),
            pos_data={"relx": 0.07, "rely": 0.01},
            border_w=0,
            hover=False,
            cmd=self.move_navbar,
        )
        self.home_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("home.png", (23, 23)),
            pos_data={"relx": 0.07, "rely": 0.2},
            border_w=0,
            hover=False,
            cmd=self.display_home_frame,
        )
        self.key_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("key.png", (23, 23)),
            pos_data={"relx": 0.07, "rely": 0.3},
            border_w=0,
            hover=False,
            cmd=self.display_key_frame,
        )
        self.passwd_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("lock.png", (24, 24)),
            pos_data={"relx": 0.05, "rely": 0.4},
            border_w=0,
            hover=False,
            cmd=self.display_passwd_frame,
        )

    def move_navbar(self):
        if not self.navbar_frame.in_start_pos:
            self.home_btn.configure(text="")
            self.key_btn.configure(text="")
            self.passwd_btn.configure(text="")
            return self.navbar_frame.move_backward()
        self.home_btn.configure(text="Home", font=("Inter", 16))
        self.key_btn.configure(text="Keys Manager", font=("Inter", 16))
        self.passwd_btn.configure(text="Passwords Manager", font=("Inter", 16))
        return self.navbar_frame.move_forward()

    def display_home_frame(self) -> None:
        self.navbar_frame.switch_indication(self.home_lbl)
        HomeFrame(self.window)

    def display_key_frame(self) -> None:
        self.navbar_frame.switch_indication(self.keys_lbl)
        KeysManagerFrame(self.window)

    def display_passwd_frame(self) -> None:
        self.navbar_frame.switch_indication(self.passwds_lbl)
        PasswordsManagerFrame(self.window)


class HomeFrame:
    def __init__(self, master: Gui):
        self.window = master
        self.home_frame = self.window.create_frame(
            pos_data={"relx": 0.08, "relheight": 1, "relwidth": 0.92},
            border_w=0,
        )

        self.window.create_label(
            master=self.home_frame,
            pos_data={
                "relx": 0.5,
                "rely": 0.3,
                "anchor": "center",
            },
            txt=f"Welcome to Password Manager, {cfg.CURRENT_USER}",
            font=("Inter", 28),
        )
        self.window.create_label(
            master=self.home_frame,
            pos_data={
                "relx": 0.5,
                "rely": 0.4,
                "anchor": "center",
            },
            txt="If you like the project support it on GitHub",
            font=("Inter", 25),
        )
        self.window.create_button(
            master=self.home_frame,
            pos_data={"relx": 0.5, "rely": 0.6, "anchor": "center"},
            img_data=("github.png", (64, 64)),
            border_w=0,
            hover=False,
            cmd=lambda: webbrowser.open(cfg.PROJECT_URL),
        )
        self.window.create_label(
            txt=f"Version: {cfg.VERSION}",
            font=("Inter", 13),
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
        )


class KeysManagerFrame:
    def __init__(self, master: Gui):
        self.window = master
        self.key_frame = self.window.create_frame(
            pos_data={"relx": 0.08, "relheight": 1, "relwidth": 0.92},
            border_w=0,
        )

        self.window.create_label(
            master=self.key_frame,
            pos_data={
                "relx": 0.5,
                "rely": 0.1,
                "anchor": "center",
            },
            txt="Key Manager",
            font=("Inter", 28),
        )
        # KEYS MANAGER BUTTONS
        self.window.create_button(
            master=self.key_frame,
            txt="Generate Key",
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
            cmd=lambda: self.window.open_toplevel_window(EnrollKey(self.window).window),
        )
        self.window.create_button(
            master=self.key_frame,
            txt="Load Key",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=self.load_key,
        )
        self.lbl_pkey = self.window.create_label(
            master=self.key_frame,
            txt=f"Current Key:\n{self.window.values.get("pkey_name")}",
            font=("Inter", 13),
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
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
        lbl_cnt = {"text": f"Current Key:\n{self.window.values.get("pkey_name")}"}
        self.window.update_label_content(lbl=self.lbl_pkey, cnt=lbl_cnt)
        if self.window.values.get("passwds"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )


class PasswordsManagerFrame:
    def __init__(self, master: Gui):
        self.window = master
        self.passwd_frame = self.window.create_frame(
            pos_data={"relx": 0.08, "relheight": 1, "relwidth": 0.92},
            border_w=0,
        )

        self.window.create_label(
            master=self.passwd_frame,
            pos_data={
                "relx": 0.5,
                "rely": 0.1,
                "anchor": "center",
            },
            txt="Password Manager",
            font=("Inter", 28),
        )

        # PASSWORDS MANAGER BUTTONS
        self.window.create_button(
            master=self.passwd_frame,
            txt="Load Passwords",
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
            cmd=self.load_passwords,
        )
        self.window.create_button(
            master=self.passwd_frame,
            txt="Save Password",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=self.store_password,
        )
        self.search_btn = self.window.create_button(
            master=self.passwd_frame,
            txt="Search Password",
            pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
            cmd=self.search_password,
            state="disabled",
        )
        self.lbl_passwd = self.window.create_label(
            master=self.passwd_frame,
            txt=f"Current Passwords:\n{self.window.values.get("passwds_name")}",
            font=("Inter", 13),
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
        )

    def load_passwords(self) -> None:
        file_p = FileManager.get_file(gui=self.window)
        if not file_p:
            return None
        FileManager.load_passwords_file(file_p=file_p, gui=self.window)
        lbl_cnt = {
            "text": f"Current Passwords:\n{self.window.values.get("passwds_name")}"
        }
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)
        if self.window.values.get("pkey"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )

    def store_password(self) -> None:
        gui = StoreService(self.window, "Save Password")
        self.window.open_toplevel_window(gui.window)
        lbl_cnt = {
            "text": f"Cuurent Passwords:\n{self.window.values.get("passwds_name")}"
        }
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)
        if self.window.values.get("pkey") and self.window.values.get("passwds"):
            self.window.update_button_content(
                btn=self.search_btn, cnt={"state": "normal"}
            )

    def search_password(self) -> None:
        read_success = FileManager.read_storefile(self.window)
        if not read_success:
            return None
        dec_success = KeyManager.decrypt_message(self.window)
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
            pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"}, show_text="*"
        )
        match = self.window.create_entry(
            pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"}, show_text="*"
        )
        self.window.create_button(
            txt="Confirm",
            pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
            cmd=lambda: KeyManager.pkey_password_match(
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
            pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"}, show_text="*"
        )
        self.window.create_button(
            txt="Confirm",
            pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"},
            cmd=lambda: KeyManager.get_pkey(
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
            pos_data={"relx": 0.8, "rely": 0.3, "anchor": "center"}, show_text="*"
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
            cmd=lambda: FileManager.write_storefile(
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
            cmd=lambda: FileManager.update_password(
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
        FileManager.search_password(
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
        FileManager.delete_password(r_gui=self.window.master, gui=self.window)
        box_cnt = {"index": "0.0", "text": ""}
        self.window.update_textbox_content(box=self.passwd_found_box, cnt=box_cnt)
        del self.window.values["passwd_found"]
