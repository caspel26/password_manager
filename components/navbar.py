from typing import Any

import customtkinter as ctk

from .gui import Gui, TopLevelGui


class AnimatedNavbar(ctk.CTkFrame):
    def __init__(
        self,
        master: Gui | TopLevelGui,
        min_width: float,
        max_width: float,
        pos_data: dict[str, Any],
        corner_r: int = 0,
        border_w: int = 1,
        fg_c: str = "transparent",
        border_c: str = None
    ):
        super().__init__(master)
        self.window = master
        self.min_w = min_width
        self.max_w = max_width
        self.pos = self.min_w
        self.in_start_pos = True
        self._corner_radius = corner_r
        self._border_width = border_w
        self._fg_color = fg_c
        self._border_color = border_c

        self.place(**pos_data)

    def switch_indication(self, lbl: ctk.CTkLabel) -> None:
        # SWITCH LIGHT ON A BUTTON WHEN IT IS CLICKED
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(bg_color="transparent")
        lbl.configure(bg_color="#bd6cff")

    def move_forward(self):
        # ANIMATE FORWARD MOVEMENT OF THE NAVBAR WHEN NAVBAR BUTTON IS CLICKED
        if self.pos < self.max_w:
            self.pos += 0.008
            self.place(relwidth=self.pos, relheight=1)
            # DISPLAY NAVBAR ABOVE OTHER COMPONENTS
            self.lift()
            self.focus_set()
            self.window.after(10, self.move_forward)
        else:
            self.in_start_pos = False

    def move_backward(self):
        # ANIMATE BACKWARD MOVEMENT OF THE NAVBAR WHEN NAVBAR BUTTON IS CLICKED
        if self.pos > self.min_w:
            self.pos -= 0.008
            self.place(relwidth=self.pos, relheight=1)
            self.window.after(10, self.move_backward)
        else:
            self.in_start_pos = True
