import webbrowser
from typing import Any

import customtkinter as ctk

from . import config as cfg
from . import KeyManager, FileManager, PasswordManager
from components import Gui, AnimatedNavbar, AnimatedFrame


class App:
    def __init__(self) -> None:
        self.window = Gui(title="Password Manager", resizable=(False, False))
        self.navbar = Navbar(self.window)


class MainLabel(ctk.CTkLabel):
    def __init__(self, master: Any):
        super().__init__(master)
        self.master = master
        self.place(relx=0.08, rely=0)
        self.configure(
            image=Gui.get_icon(("bg.jpg", (800, 600))), width=800, height=600
        )


class MainFrame(AnimatedFrame):
    def __init__(self, master: Any):
        super().__init__(
            master=master,
            pos_data={"relx": 1, "rely": 0.2, "relheight": 0.7, "relwidth": 0.92},
            max_x=0,
        )


class Navbar:
    def __init__(self, master: Gui) -> None:
        self.window = master
        self.main_label = MainLabel(self.window)

        self.navbar_frame = AnimatedNavbar(
            master=self.window,
            pos_data={"relx": 0, "relheight": 1, "relwidth": 0.08},
            min_width=0.08,
            max_width=0.3,
            fg_c="#818afb",
        )

        # NAVBAR LABELS
        self.home_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": 0.01, "rely": 0.2},
        )
        self.keys_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": 0.01, "rely": 0.3},
        )
        self.passwds_lbl = self.window.create_label(
            master=self.navbar_frame,
            pos_data={"relx": 0.01, "rely": 0.4},
        )

        # NAVBAR BUTTONS
        self.navbar_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("navbar.png", (25, 25)),
            pos_data={"relx": 0.07, "rely": 0.01},
            border_w=0,
            fg_color="transparent",
            cmd=self.move_navbar,
        )
        self.home_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("home.png", (23, 23)),
            pos_data={"relx": 0.07, "rely": 0.2},
            border_w=0,
            cmd=self.display_home_frame,
            fg_color="transparent",
        )
        self.key_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("key.png", (25, 25)),
            pos_data={"relx": 0.07, "rely": 0.3},
            border_w=0,
            cmd=self.display_key_frame,
            fg_color="transparent",
        )
        self.passwd_btn = self.window.create_button(
            master=self.navbar_frame,
            img_data=("lock.png", (25, 25)),
            pos_data={"relx": 0.07, "rely": 0.4},
            border_w=0,
            cmd=self.display_passwd_frame,
            fg_color="transparent",
        )

    def populate_navbar_buttons(self):
        if not self.navbar_frame.in_start_pos:
            self.home_btn.configure(text="")
            self.key_btn.configure(text="")
            self.passwd_btn.configure(text="")
            return None
        self.home_btn.configure(text="Home", font=("Inter", 16))
        self.key_btn.configure(text="Key Manager", font=("Inter", 16))
        self.passwd_btn.configure(text="Password Manager", font=("Inter", 16))

    def move_navbar(self):
        btn_w = 25
        btn_h = 25
        if self.navbar_frame.in_start_pos:
            self.navbar_frame.open()
            self.navbar_btn.configure(
                image=self.window.get_icon(("close.png", (btn_w, btn_h))),
                width=btn_w,
                height=btn_h,
            )
        else:
            self.navbar_frame.close()
            self.navbar_btn.configure(
                image=self.window.get_icon(("navbar.png", (btn_w, btn_h))),
                width=btn_w,
                height=btn_h,
            )
        return self.populate_navbar_buttons()

    def display_home_frame(self) -> None:
        if not self.navbar_frame.in_start_pos:
            self.move_navbar()
        self.navbar_frame.switch_indication(self.home_lbl)
        HomeFrame(self.window, self.main_label)

    def display_key_frame(self) -> None:
        if not self.navbar_frame.in_start_pos:
            self.move_navbar()
        self.navbar_frame.switch_indication(self.keys_lbl)
        KeysManagerFrame(self.window, self.main_label)

    def display_passwd_frame(self) -> None:
        if not self.navbar_frame.in_start_pos:
            self.move_navbar()
        self.navbar_frame.switch_indication(self.passwds_lbl)
        PasswordsManagerFrame(self.window, self.main_label)


class HomeFrame:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel):
        self.window = master
        self.main_label = main_label
        self.home_frame = self.window.create_frame(
            master=self.main_label,
            pos_data={"relx": 0, "rely": 0.2, "relheight": 0.7, "relwidth": 0.92},
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
            pos_data={
                "relx": 0.5,
                "rely": 0.6,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            img_data=("github.png", (25, 25)),
            border_w=0,
            txt="GitHub",
            cmd=lambda: webbrowser.open(cfg.PROJECT_URL),
            font=("Inter", 20),
        )
        self.window.create_label(
            master=self.home_frame,
            txt=f"Version: {cfg.VERSION}",
            font=("Inter", 14),
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
        )


class KeysManagerFrame:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel):
        self.window = master
        self.main_label = main_label
        self.key_frame = self.window.create_frame(
            master=self.main_label,
            pos_data={"relx": 0, "rely": 0.2, "relheight": 0.7, "relwidth": 0.92},
            border_w=0,
        )

        # KEYS MANAGER BUTTONS
        self.window.create_button(
            master=self.key_frame,
            txt="Generate Key",
            pos_data={
                "relx": 0.3,
                "rely": 0.25,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=EnrollKey(
                master=self.window, main_label=self.main_label
            ).main_frame.move_backward,
            img_data=("key.png", (30, 30)),
            font=("Inter", 14),
        )
        self.window.create_button(
            master=self.key_frame,
            txt="Load Key",
            pos_data={
                "relx": 0.7,
                "rely": 0.25,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.load_key,
            img_data=("load.png", (30, 30)),
            font=("Inter", 14),
        )
        self.window.values |= {
            "pkey_lbl": self.window.create_label(
                master=self.key_frame,
                txt=f"Current Key:\n{self.window.values.get("pkey_name")}",
                font=("Inter", 13),
                pos_data={
                    "relx": 0.08,
                    "rely": 0.95,
                    "anchor": "center",
                    "relwidth": 0.35,
                },
            )
        }

    def load_key(self) -> None:
        self.window.values["key_file"] = ctk.filedialog.askopenfilename(
            title="Select Key File",
            filetypes=cfg.FILES_TYPE,
            defaultextension=cfg.FILES_TYPE,
        )
        if not self.window.values.get("key_file"):
            return self.window.show_messages("Error", "Invalid file")
        LoadKey(self.window, self.main_label).main_frame.move_backward()


class PasswordsManagerFrame:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel):
        self.window = master
        self.main_label = main_label
        self.passwd_frame = self.window.create_frame(
            master=self.main_label,
            pos_data={"relx": 0, "rely": 0.2, "relheight": 0.7, "relwidth": 0.92},
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
            pos_data={
                "relx": 0.2,
                "rely": 0.25,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.load_passwords,
            img_data=("load.png", (30, 30)),
            font=("Inter", 14),
        )
        self.window.create_button(
            master=self.passwd_frame,
            txt="Save Password",
            pos_data={
                "relx": 0.5,
                "rely": 0.25,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.store_password,
            img_data=("save.png", (25, 25)),
            font=("Inter", 14),
        )
        self.search_btn = self.window.create_button(
            master=self.passwd_frame,
            txt="Search Password",
            pos_data={
                "relx": 0.8,
                "rely": 0.25,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.search_password,
            state="disabled",
            img_data=("search.png", (25, 25)),
            font=("Inter", 14),
        )
        self.generate_passwd_btn = self.window.create_button(
            master=self.passwd_frame,
            txt="Generate Password",
            pos_data={
                "relx": 0.5,
                "rely": 0.4,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.generate_password,
            img_data=("lock.png", (25, 25)),
            font=("Inter", 14),
        )
        self.lbl_passwd = self.window.create_label(
            master=self.passwd_frame,
            txt=f"Current Passwords:\n{self.window.values.get("passwds_name")}",
            font=("Inter", 13),
            pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
        )
        self.gen_passwd_box = self.window.create_textbox(
            master=self.passwd_frame,
            data={"index": "0.0", "text": f"Password Generated:\n{None}"},
            pos_data={
                "relx": 0.15,
                "rely": 1.07,
                "anchor": "center",
                "relwidth": 0.35,
            },
            font=("Inter", 13),
        )
        self.activate_button()

    def activate_button(self):
        if self.window.values.get("pkey") and self.window.values.get("passwds"):
            self.search_btn.configure(state="normal")
        self.window.after(100, self.activate_button)

    def load_passwords(self) -> None:
        file_p = FileManager.get_file(self.window)
        if not file_p:
            return None
        FileManager.load_passwords_file(file_p=file_p, gui=self.window)
        lbl_cnt = {
            "text": f"Current Passwords:\n{self.window.values.get("passwds_name")}"
        }
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)

    def store_password(self) -> None:
        StoreService(self.window, self.main_label).main_frame.move_backward()
        lbl_cnt = {
            "text": f"Cuurent Passwords:\n{self.window.values.get("passwds_name")}"
        }
        self.window.update_label_content(lbl=self.lbl_passwd, cnt=lbl_cnt)

    def search_password(self) -> None:
        read_success = FileManager.read_storefile(self.window)
        if not read_success:
            return None
        dec_success = KeyManager.decrypt_message(self.window)
        if not dec_success:
            return None
        SearchService(self.window, self.main_label).main_frame.move_backward()

    def generate_password(self) -> None:
        passwd = PasswordManager.gen_password(self.window)
        box_cnt = {
            "index": "0.0",
            "text": f"Passwords Generated:\n{passwd}",
        }
        self.window.update_textbox_content(self.gen_passwd_box, box_cnt)


class EnrollKey:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        self.window = master
        self.main_frame = MainFrame(main_label)
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Password",
            pos_data={"relx": 0.3, "rely": 0.15, "anchor": "center"},
        )
        self.window.create_label(
            master=self.main_frame,
            txt="Confirm Password",
            pos_data={"relx": 0.7, "rely": 0.15, "anchor": "center"},
        )
        passwd = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.3, "rely": 0.25, "anchor": "center"},
            show_text="*",
        )
        match = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.7, "rely": 0.25, "anchor": "center"},
            show_text="*",
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Confirm",
            cmd=lambda: KeyManager.pkey_password_match(
                passwd=passwd.get(),
                passwd_match=match.get(),
                gui=self.window,
            ),
            pos_data={
                "relx": 0.5,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            font=("Inter", 14),
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Go Back",
            pos_data={
                "relx": 0.5,
                "rely": 0.9,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.main_frame.move_forward,
            font=("Inter", 14),
        )


class LoadKey:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        self.window = master
        self.main_frame = MainFrame(main_label)
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Password",
            pos_data={"relx": 0.5, "rely": 0.2, "anchor": "center"},
        )
        self.passwd = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
            show_text="*",
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Confirm",
            pos_data={
                "relx": 0.5,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=lambda: KeyManager.get_pkey(
                file_p=self.window.values.get("key_file"),
                passwd=self.passwd.get(),
                gui=self.window,
            ),
            font=("Inter", 14),
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Go Back",
            pos_data={
                "relx": 0.5,
                "rely": 0.9,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.main_frame.move_forward,
            font=("Inter", 14),
        )


class AddService:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        self.window = master
        self.main_frame = MainFrame(main_label)
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Service",
            pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"},
        )
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Username",
            pos_data={"relx": 0.5, "rely": 0.2, "anchor": "center"},
        )
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Password",
            pos_data={"relx": 0.8, "rely": 0.2, "anchor": "center"},
        )
        self.service = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"},
        )
        self.username = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
        )
        self.passwd = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.8, "rely": 0.3, "anchor": "center"},
            show_text="*",
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Go Back",
            pos_data={
                "relx": 0.5,
                "rely": 0.9,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.main_frame.move_forward,
            font=("Inter", 14),
        )


class StoreService(AddService):
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        super().__init__(master, main_label)

        self.window.create_button(
            master=self.main_frame,
            txt="Save & Encrypt",
            pos_data={
                "relx": 0.5,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=lambda: FileManager.write_storefile(
                gui=self.window,
                payload={
                    "service": self.service.get(),
                    "username": self.username.get(),
                    "password": self.passwd.get(),
                },
            ),
            font=("Inter", 14),
        )


class UpdateService(AddService):
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        super().__init__(master, main_label)

        self.window.create_button(
            master=self.main_frame,
            txt="Update & Encrypt",
            pos_data={
                "relx": 0.2,
                "rely": 0.9,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=lambda: FileManager.update_password(
                gui=self.window,
                payload={
                    "service": self.service.get(),
                    "username": self.username.get(),
                    "password": self.passwd.get(),
                },
            ),
            font=("Inter", 14),
        )


class SearchService:
    def __init__(self, master: Gui, main_label: ctk.CTkLabel) -> None:
        self.window = master
        self.main_label = main_label
        self.main_frame = MainFrame(main_label)
        self.window.create_label(
            master=self.main_frame,
            txt="Enter Service",
            pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"},
        )
        self.service = self.window.create_entry(
            master=self.main_frame,
            pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"},
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Search",
            pos_data={
                "relx": 0.2,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.search_password,
            font=("Inter", 14),
        )
        self.updated_passwd_btn = self.window.create_button(
            master=self.main_frame,
            txt="Update Password",
            pos_data={
                "relx": 0.5,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=lambda: UpdateService(
                self.window, self.main_label
            ).main_frame.move_backward(),
            state="disabled",
            font=("Inter", 14),
        )
        self.delete_passwd_btn = self.window.create_button(
            master=self.main_frame,
            txt="Delete Password",
            pos_data={
                "relx": 0.8,
                "rely": 0.7,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=lambda: FileManager.delete_password(self.window),
            state="disabled",
            font=("Inter", 14),
        )
        self.window.create_button(
            master=self.main_frame,
            txt="Go Back",
            pos_data={
                "relx": 0.5,
                "rely": 0.9,
                "anchor": "center",
                "relwidth": 0.25,
                "relheight": 0.08,
            },
            cmd=self.main_frame.move_forward,
            font=("Inter", 14),
        )
        self.window.values |= {
            "passwd_found_box": self.window.create_textbox(
                master=self.main_frame,
                pos_data={"relx": 0.8, "rely": 0.4, "anchor": "center"},
                data={"index": "0.0", "text": ""},
            )
        }

    def search_password(self) -> None:
        FileManager.search_password(service=self.service.get(), gui=self.window)
        self.updated_passwd_btn.configure(state="normal")
        self.delete_passwd_btn.configure(state="normal")
