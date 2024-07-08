from typing import Callable, Any, Optional

import customtkinter as ctk
from PIL import ImageTk, Image
from CTkMessagebox import CTkMessagebox

from src import config as cfg


class BaseGui:
    def __init__(self) -> None:
        self.toplevel_window: Optional[TopLevelGui] = None
        super(BaseGui, self).__init__()

    def create_frame(
        self,
        pos_data: dict[str, Any],
        master: Any | None = None,
        corner_r: int = 0,
        border_w: int = 1,
        fg_c: str = "transparent",
    ) -> ctk.CTkFrame:
        if master is None:
            master = self
        frame = ctk.CTkFrame(
            master=master,
            corner_radius=corner_r,
            border_width=border_w,
            fg_color=fg_c,
        )
        frame.place(**pos_data)
        return frame

    def create_button(
        self,
        pos_data: dict[str, str | float],
        state: str = "normal",
        txt: str | None = None,
        master: Any | None = None,
        txt_c: str | None = None,
        cmd: Callable | None = None,
        corner_r: int = 32,
        fg_color: str = "transparent",
        border_w: int = 2,
        border_c: str = "#bd6cff",
        img_data: tuple[str, tuple[int, int]] | None = None,
        hover: bool = True,
    ) -> ctk.CTkButton:
        if master is None:
            master = self
        btn = ctk.CTkButton(
            master,
            corner_radius=corner_r,
            text=txt,
            text_color=txt_c,
            command=cmd,
            fg_color=fg_color,
            border_color=border_c,
            border_width=border_w,
            state=state,
            hover=hover,
        )
        if img_data:
            w, h = img_data[1]
            btn.configure(image=self.get_icon(img_data), width=w, height=h)
        btn.place(**pos_data)
        return btn

    def create_label(
        self,
        pos_data: dict[str, str | float],
        master: Any | None = None,
        txt: str | None = None,
        txt_c: str | None = None,
        font: tuple[str, int] | None = None,
        corner_r: int = 2,
        bg_color: str = "transparent",
    ) -> ctk.CTkLabel:
        if master is None:
            master = self
        lbl = ctk.CTkLabel(
            master,
            corner_radius=corner_r,
            text=txt,
            text_color=txt_c,
            bg_color=bg_color,
            font=font,
        )
        lbl.place(**pos_data)
        return lbl

    def create_entry(
        self,
        pos_data: dict[str, str | float],
        master: Any | None = None,
        txt_c: str | None = None,
        show_text: str | None = None,
        corner_r: int = 2,
    ) -> ctk.CTkEntry:
        if master is None:
            master = self
        entry = ctk.CTkEntry(
            master, corner_radius=corner_r, text_color=txt_c, show=show_text
        )
        entry.place(**pos_data)
        return entry

    def create_tabs(self, size: dict[str, int], tabs: list[str]) -> ctk.CTkTabview:
        t = ctk.CTkTabview(self, **size)
        t.pack(padx=20, pady=20)
        for tab in tabs:
            t.add(tab)
        return t

    def create_textbox(
        self,
        pos_data: dict[str, str | float],
        data: dict[str, str],
        master: Any | None = None,
        corner_r: int = 32,
        fg_color: str = "transparent",
        font: tuple[str, int] | None = None,
    ) -> ctk.CTkTextbox:
        if master is None:
            master = self
        box = ctk.CTkTextbox(
            master, corner_radius=corner_r, fg_color=fg_color, font=font
        )
        box.place(**pos_data)
        box.insert(**data)
        return box

    def open_toplevel_window(self, window: "TopLevelGui") -> None:
        if self.toplevel_window is None or self.toplevel_window.winfo_exists():
            # create window if its None or destroyed
            self.toplevel_window = window

    def show_messages(self, title: str, msg: str) -> None:
        icon_name = None
        match title:
            case "Error":
                icon_name = "cancel"
            case "Success":
                icon_name = "check"

        return CTkMessagebox(
            master=self,
            title=title,
            message=msg,
            icon=title.lower() if not icon_name else icon_name,
            fade_in_duration=1,
            sound=True,
        )

    @classmethod
    def update_label_content(cls, lbl: ctk.CTkLabel, cnt: dict) -> ctk.CTkLabel:
        lbl.configure(**cnt)
        return lbl

    @classmethod
    def update_button_content(cls, btn: ctk.CTkButton, cnt: dict) -> ctk.CTkButton:
        btn.configure(**cnt)
        return btn

    @classmethod
    def update_textbox_content(cls, box: ctk.CTkTextbox, cnt: dict) -> ctk.CTkTextbox:
        box.delete(cnt["index"], "end")
        box.insert(**cnt)
        return box

    @classmethod
    def get_size(cls, size: str) -> str:
        for s in cfg.DEFAULT_GUI_SIZES:
            if size != s[0]:
                continue
            return s[1]
        return size

    @classmethod
    def get_icon(cls, data: tuple[str, tuple[int, int]]) -> ctk.CTkImage:
        icon = cfg.IMG_DIR / data[0]
        try:
            img = Image.open(icon)
        except FileNotFoundError as e:
            CTkMessagebox(
                title="Error",
                message=f"IMAGE: {e}",
                icon="error",
                fade_in_duration=0.2,
                sound=True,
            )
            exit(1)
        ctk_icon = ctk.CTkImage(dark_image=img, size=data[1])
        return ctk_icon


class Gui(ctk.CTk, BaseGui):
    def __init__(
        self,
        title: str,
        resizable: tuple[bool, bool],
        size: str = "primary",
    ):
        super().__init__()
        BaseGui.__init__(self)

        w, h = resizable
        self.values: dict[str, Any] = {}
        self.geometry(self.get_size(size))
        self.title(title)
        self.resizable(w, h)
        self._set_appearance_mode("dark")
        self.icon = ImageTk.PhotoImage(file=cfg.ICON)
        self.wm_iconbitmap()
        self.iconphoto(False, self.icon)


class TopLevelGui(ctk.CTkToplevel, BaseGui):
    def __init__(
        self,
        master: Gui,
        title: str,
        resizable: tuple[bool, bool],
        size: str = "secondary",
    ):
        super().__init__()
        BaseGui.__init__(self)

        w, h = resizable
        self.master = master
        self.values: dict[str, Any] = {}
        self.geometry(self.get_size(size))
        self.title(title)
        self.resizable(w, h)
        self._set_appearance_mode("dark")
        self.icon = ImageTk.PhotoImage(file=cfg.ICON)
        self.wm_iconbitmap()
        self.after(300, lambda: self.iconphoto(False, self.icon))

    def lock_main_window(self) -> None:
        self.transient(self.master)
        self.master.wait_window(self)

    def close_window(self) -> None:
        self.destroy()
        self.update()
