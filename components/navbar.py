import customtkinter as ctk

from .widgets import AnimatedFrame


class AnimatedNavbar(AnimatedFrame):
    def switch_indication(self, lbl: ctk.CTkLabel) -> None:
        # SWITCH LIGHT ON A BUTTON WHEN IT IS CLICKED
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(bg_color="transparent")
        lbl.configure(bg_color="#bd6cff")

