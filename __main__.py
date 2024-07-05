import customtkinter as ctk

import src.config as cfg
from src.gui import App
from src.serialize import Key, File

# root = Gui(size="primary", title="Password Manager", resizable=(False, False))


# def key_gen() -> None:
#     passwd_gui = Gui(
#         size="secondary", title="Generate Private Key", resizable=(False, False)
#     )
#     passwd_gui.create_label(
#         txt="Enter Password", pos_data={"relx": 0.3, "rely": 0.2, "anchor": "center"}
#     )
#     passwd_gui.create_label(
#         txt="Confirm Password", pos_data={"relx": 0.7, "rely": 0.2, "anchor": "center"}
#     )
#     passwd = passwd_gui.create_entry(
#         pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"}
#     )
#     passwd_match = passwd_gui.create_entry(
#         pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"}
#     )
#     passwd_gui.create_button(
#         txt="Confirm",
#         pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
#         cmd=lambda: Key.pkey_password_match(
#             passwd=passwd.get(), passwd_match=passwd_match.get(), gui=passwd_gui
#         ),
#     )
#     passwd_gui.create_button(
#         txt="Exit",
#         pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
#         cmd=passwd_gui.destroy,
#     )
#     passwd_gui.mainloop()


# def load_key():
#     file_p = ctk.filedialog.askopenfilename(
#         title="Select Key File",
#         filetypes=cfg.FILES_TYPE,
#         defaultextension=cfg.FILES_TYPE,
#     )
#     key_gui = Gui(size="secondary", title="Load Private Key", resizable=(False, False))
#     key_gui.create_label(
#         txt="Enter Password", pos_data={"relx": 0.1, "rely": 0.3, "anchor": "center"}
#     )
#     passwd = key_gui.create_entry(
#         pos_data={"relx": 0.3, "rely": 0.3, "anchor": "center"}
#     )
#     key_gui.create_button(
#         txt="Confirm",
#         pos_data={"relx": 0.7, "rely": 0.3, "anchor": "center"},
#         cmd=lambda: Key.get_pkey(
#             file_p=file_p, passwd=passwd.get(), r_gui=root, gui=key_gui
#         ),
#     )
#     key_gui.create_button(
#         txt="Exit",
#         pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
#         cmd=key_gui.destroy,
#     )
#     key_gui.mainloop()


# def add_service_gui() -> tuple[Gui, list[ctk.CTkEntry]]:
#     gui = Gui(size="secondary", title="Save Password", resizable=(False, False))
#     gui.create_label(
#         txt="Enter Service", pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"}
#     )
#     gui.create_label(
#         txt="Enter Username", pos_data={"relx": 0.5, "rely": 0.2, "anchor": "center"}
#     )
#     gui.create_label(
#         txt="Enter Password", pos_data={"relx": 0.8, "rely": 0.2, "anchor": "center"}
#     )
#     service = gui.create_entry(pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"})
#     username = gui.create_entry(pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"})
#     passwd = gui.create_entry(pos_data={"relx": 0.8, "rely": 0.3, "anchor": "center"})
#     gui.create_button(
#         txt="Exit",
#         pos_data={"relx": 0.8, "rely": 0.7, "anchor": "center"},
#         cmd=gui.destroy,
#     )
#     service_info = [service, username, passwd]
#     return gui, service_info


# def store_password() -> None:
#     passwd_gui, service_info = add_service_gui()
#     passwd_gui.create_button(
#         txt="Encrypt Data",
#         pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: Key.encrypt_message(
#             gui=passwd_gui,
#             r_gui=root,
#             payload={
#                 "service": service_info[0].get(),
#                 "username": service_info[1].get(),
#                 "password": service_info[2].get(),
#             },
#         ),
#     )
#     passwd_gui.create_button(
#         txt="Save",
#         pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: File.write_storefile(gui=passwd_gui, r_gui=root),
#     )
#     passwd_gui.mainloop()


# def load_passwords():
#     file_p = File.get_file(gui=root)
#     File.load_passwords_file(file_p=file_p, gui=root)


# def update_password(gui: Gui) -> None:
#     passwd_gui, service_info = add_service_gui()
#     passwd_gui.create_button(
#         txt="Update & Encrypt",
#         pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: File.update_password(
#             r_gui=root,
#             gui=passwd_gui,
#             main_gui=gui,
#             payload={
#                 "service": service_info[0].get(),
#                 "username": service_info[1].get(),
#                 "password": service_info[2].get(),
#             },
#         ),
#     )
#     passwd_gui.mainloop()


# def search_password() -> None:
#     passwd_gui = Gui(
#         size="secondary", title="Search Password", resizable=(False, False)
#     )
#     passwd_gui.create_label(
#         txt="Enter Service", pos_data={"relx": 0.2, "rely": 0.2, "anchor": "center"}
#     )
#     service = passwd_gui.create_entry(
#         pos_data={"relx": 0.2, "rely": 0.3, "anchor": "center"}
#     )
#     File.read_storefile(r_gui=root, gui=passwd_gui)
#     Key.decrypt_message(r_gui=root, gui=passwd_gui)
#     passwd_gui.create_button(
#         txt="Search",
#         pos_data={"relx": 0.2, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: File.search_password(
#             service=service.get(), r_gui=root, gui=passwd_gui
#         ),
#     )
#     passwd_gui.create_button(
#         name="update_password",
#         txt="Update Password",
#         pos_data={"relx": 0.5, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: update_password(gui=passwd_gui),
#         state="disabled",
#     )
#     passwd_gui.create_button(
#         name="delete_password",
#         txt="Delete Password",
#         pos_data={"relx": 0.8, "rely": 0.7, "anchor": "center"},
#         cmd=lambda: File.delete_password(r_gui=root, gui=passwd_gui),
#         state="disabled",
#     )
#     passwd_gui.create_button(
#         txt="Exit",
#         pos_data={"relx": 0.5, "rely": 0.9, "anchor": "center"},
#         cmd=passwd_gui.destroy,
#     )
#     passwd_gui.mainloop()


# def main():
#     # TABS
#     root.create_tabs(
#         {"width": 700, "height": 500}, ["Keys Manager", "Passwords Manager"]
#     )
#     KEYS_MANAGER_TAB = root.tabs["Keys Manager"]
#     PASSWDS_MANAGER_TAB = root.tabs["Passwords Manager"]

#     # GUI INFO LABELS
#     root.create_label(
#         name="key_info",
#         txt=f"Key: {root.values.get("pkey_name")}",
#         pos_data={"relx": 0.061, "rely": 0.90, "anchor": "center"},
#     )
#     root.create_label(
#         name="passwd_info",
#         txt=f"Passwords: {root.values.get("passwds_name")}",
#         pos_data={"relx": 0.09, "rely": 0.95, "anchor": "center"},
#     )
#     root.create_label(
#         txt=f"Version: {cfg.VERSION}",
#         pos_data={"relx": 0.9, "rely": 0.95, "anchor": "center"},
#     )

#     # KEYS MANAGER BUTTONS
#     root.create_button(
#         master=KEYS_MANAGER_TAB,
#         txt="Generate Key",
#         pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
#         cmd=key_gen,
#     )
#     root.create_button(
#         master=KEYS_MANAGER_TAB,
#         txt="Load Key",
#         pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
#         cmd=load_key,
#     )

#     # PASSWORDS MANAGER BUTTONS
#     root.create_button(
#         master=PASSWDS_MANAGER_TAB,
#         txt="Load Passwords",
#         pos_data={"relx": 0.5, "rely": 0.1, "anchor": "center"},
#         cmd=load_passwords,
#     )
#     root.create_button(
#         master=PASSWDS_MANAGER_TAB,
#         txt="Save Password",
#         pos_data={"relx": 0.5, "rely": 0.3, "anchor": "center"},
#         cmd=store_password,
#     )
#     root.create_button(
#         master=PASSWDS_MANAGER_TAB,
#         txt="Search Password",
#         pos_data={"relx": 0.5, "rely": 0.5, "anchor": "center"},
#         cmd=search_password,
#     )

#     # MAINLOOP
#     root.mainloop()

def main():
    root = App()
    root.window.mainloop()


if __name__ == "__main__":
    main()
