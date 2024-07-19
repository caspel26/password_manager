from typing import Any

import customtkinter as ctk


class AnimatedFrame(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        pos_data: dict[str, Any],
        min_width: float | None = None,
        max_width: float | None = None,
        max_y: float | None = None,
        max_x: float | None = None,
        corner_r: int = 0,
        border_w: int = 1,
        fg_c: str = "transparent",
        bg_c: str = "#242424",
        border_c: str = None,
    ):
        super().__init__(master)
        self.master = master
        self.min_w = min_width
        self.max_w = max_width
        self.pos = self.min_w
        self.in_start_pos = True
        self._corner_radius = corner_r
        self._border_width = border_w
        self._fg_color = fg_c
        self._border_color = border_c
        self._bg_color = bg_c
        self.place(**pos_data)
        self.end_y = max_y
        self.end_x = max_x
        self.start_y = None
        self.start_x = None

        if pos_data.get("rely") is not None:
            self.start_y = pos_data["rely"]
        if pos_data.get("relx") is not None:
            self.start_x = pos_data["relx"]
        
        self.pos_y = self.start_y
        self.pos_x = self.start_x

    def open(self):
        # ANIMATE FORWARD MOVEMENT OF THE WIDGET USING WIDTH
        if self.pos < self.max_w:
            self.pos += 0.008
            self.place(relwidth=self.pos, relheight=1)
            # DISPLAY WIDGET ABOVE OTHER COMPONENTS
            self.lift()
            self.focus_set()
            self.master.after(10, self.open)
        else:
            self.in_start_pos = False

    def close(self):
        # ANIMATE BACKWARD MOVEMENT OF THE WIDGET USING WIDTH
        if self.pos > self.min_w:
            self.pos -= 0.008
            self.place(relwidth=self.pos, relheight=1)
            self.master.after(10, self.close)
        else:
            self.in_start_pos = True

    def move_upside(self):
        if self.pos_y > self.end_y:
            self.pos_y -= 0.008
            self.place(rely=self.pos_y)
            self.master.after(4, self.move_upside)
        else:
            self.in_start_pos = False

    def move_downside(self):
        if self.pos_y < self.start_y:
            self.pos_y += 0.008
            self.place(rely=self.pos_y)
            self.master.after(4, self.move_downside)
        else:
            self.in_start_pos = True

    def move_forward(self):
        if self.pos_x < self.start_x:
            self.pos_x += 0.008
            self.place(relx=self.pos_x)
            self.master.after(1, self.move_forward)
        else:
            self.in_start_pos = False

    def move_backward(self):
        if self.pos_x > self.end_x:
            self.pos_x -= 0.008
            self.place(relx=self.pos_x)
            self.master.after(1, self.move_backward)
        else:
            self.in_start_pos = True