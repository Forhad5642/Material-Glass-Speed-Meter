import tkinter as tk
from tkinter import colorchooser, messagebox
import psutil
import json
import os
import sys
import winreg
from datetime import date


# =========================================================
# FILES
# =========================================================

SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"),
    "speedmeter_settings.json"
)

DATA_FILE = os.path.join(
    os.path.expanduser("~"),
    "speedmeter_data.json"
)

STARTUP_NAME = "MaterialGlassSpeedMeter"


# =========================================================
# MAIN APP
# =========================================================

class MaterialGlassSpeedMeter:

    def __init__(self, root):

        self.root = root

        # =================================================
        # DEFAULT SETTINGS
        # =================================================

        self.width = 190
        self.height = 58

        self.min_width = 150
        self.min_height = 48

        self.padding_x = 8
        self.padding_y = 4

        self.font_size = 9

        self.background = "#202124"
        self.text_color = "#FFFFFF"
        self.accent_color = "#64B5F6"

        self.opacity = 0.88

        self.pinned = True
        self.locked = False
        self.startup = False

        # Saved position
        self.pos_x = None
        self.pos_y = None

        # =================================================
        # LOAD SETTINGS
        # =================================================

        self.load_settings()

        # =================================================
        # WINDOW
        # =================================================

        self.root.overrideredirect(True)

        self.root.attributes(
            "-topmost",
            self.pinned
        )

        self.root.attributes(
            "-alpha",
            self.opacity
        )

        self.root.configure(
            bg=self.background
        )

        # =================================================
        # POSITION
        # =================================================

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if self.pos_x is None:
            self.pos_x = screen_w - self.width - 20

        if self.pos_y is None:
            self.pos_y = screen_h - self.height - 70

        self.root.geometry(
            f"{self.width}x{self.height}"
            f"+{self.pos_x}+{self.pos_y}"
        )

        # =================================================
        # MAIN FRAME
        # =================================================

        self.frame = tk.Frame(
            self.root,
            bg=self.background,
            highlightthickness=1,
            highlightbackground=self.accent_color
        )

        self.frame.pack(
            fill="both",
            expand=True
        )

        # =================================================
        # SPEED / SYSTEM TEXT
        # =================================================

        self.label = tk.Label(
            self.frame,

            text=(
                "↓ 0 KB/s    ↑ 0 KB/s\n"
                "CPU 0%   RAM 0%   🔋 --"
            ),

            font=(
                "Segoe UI",
                self.font_size,
                "bold"
            ),

            fg=self.text_color,
            bg=self.background,

            justify="left",
            anchor="w"
        )

        self.label.pack(
            fill="both",
            expand=True,
            padx=self.padding_x,
            pady=self.padding_y
        )

        # =================================================
        # RESIZE HANDLE
        # =================================================

        self.resize_handle = tk.Label(
            self.root,
            text="◢",
            font=("Segoe UI", 7),
            fg=self.accent_color,
            bg=self.background,
            cursor="size_nw_se"
        )

        self.resize_handle.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-2,
            y=-1
        )

        self.resize_handle.bind(
            "<Button-1>",
            self.start_resize
        )

        self.resize_handle.bind(
            "<B1-Motion>",
            self.do_resize
        )

        # =================================================
        # DRAG ANYWHERE
        # =================================================

        for widget in (
            self.root,
            self.frame,
            self.label
        ):

            widget.bind(
                "<Button-1>",
                self.start_move
            )

            widget.bind(
                "<B1-Motion>",
                self.move_window
            )

            widget.bind(
                "<Button-3>",
                self.show_menu
            )

        # =================================================
        # RIGHT CLICK MENU
        # =================================================

        self.menu = tk.Menu(
            self.root,
            tearoff=0
        )

        self.update_menu()

        # =================================================
        # NETWORK COUNTER
        # =================================================

        net = psutil.net_io_counters()

        self.old_download = net.bytes_recv
        self.old_upload = net.bytes_sent

        # =================================================
        # DAILY DATA
        # =================================================

        self.load_daily_data()

        # =================================================
        # START STATS
        # =================================================

        self.update_stats()

    # =====================================================
    # SETTINGS LOAD
    # =====================================================

    def load_settings(self):

        if not os.path.exists(SETTINGS_FILE):
            return

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            self.width = data.get(
                "width",
                self.width
            )

            self.height = data.get(
                "height",
                self.height
            )

            self.padding_x = data.get(
                "padding_x",
                self.padding_x
            )

            self.padding_y = data.get(
                "padding_y",
                self.padding_y
            )

            self.font_size = data.get(
                "font_size",
                self.font_size
            )

            self.background = data.get(
                "background",
                self.background
            )

            self.text_color = data.get(
                "text_color",
                self.text_color
            )

            self.accent_color = data.get(
                "accent_color",
                self.accent_color
            )

            self.opacity = data.get(
                "opacity",
                self.opacity
            )

            self.pinned = data.get(
                "pinned",
                self.pinned
            )

            self.locked = data.get(
                "locked",
                self.locked
            )

            self.startup = data.get(
                "startup",
                self.startup
            )

            self.pos_x = data.get(
                "pos_x",
                None
            )

            self.pos_y = data.get(
                "pos_y",
                None
            )

        except Exception:
            pass

    # =====================================================
    # SETTINGS SAVE
    # =====================================================

    def save_settings(self):

        try:

            self.pos_x = self.root.winfo_x()
            self.pos_y = self.root.winfo_y()

            self.width = self.root.winfo_width()
            self.height = self.root.winfo_height()

        except Exception:
            pass

        data = {

            "width": self.width,
            "height": self.height,

            "pos_x": self.pos_x,
            "pos_y": self.pos_y,

            "padding_x": self.padding_x,
            "padding_y": self.padding_y,

            "font_size": self.font_size,

            "background": self.background,
            "text_color": self.text_color,
            "accent_color": self.accent_color,

            "opacity": self.opacity,

            "pinned": self.pinned,
            "locked": self.locked,
            "startup": self.startup
        }

        try:

            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=4
                )

        except Exception:
            pass

    # =====================================================
    # DAILY DATA LOAD
    # =====================================================

    def load_daily_data(self):

        today = str(date.today())

        self.data_date = today
        self.today_download = 0
        self.today_upload = 0

        if not os.path.exists(DATA_FILE):

            self.save_daily_data()

            return

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if data.get("date") == today:

                self.today_download = data.get(
                    "download",
                    0
                )

                self.today_upload = data.get(
                    "upload",
                    0
                )

            else:

                # New day
                self.data_date = today
                self.today_download = 0
                self.today_upload = 0

                self.save_daily_data()

        except Exception:

            self.today_download = 0
            self.today_upload = 0

    # =====================================================
    # DAILY DATA SAVE
    # =====================================================

    def save_daily_data(self):

        data = {

            "date": self.data_date,

            "download": self.today_download,

            "upload": self.today_upload
        }

        try:

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=4
                )

        except Exception:
            pass

    # =====================================================
    # DRAG
    # =====================================================

    def start_move(self, event):

        if self.locked:
            return

        self.drag_x = event.x_root
        self.drag_y = event.y_root

        self.start_window_x = (
            self.root.winfo_x()
        )

        self.start_window_y = (
            self.root.winfo_y()
        )

    def move_window(self, event):

        if self.locked:
            return

        dx = (
            event.x_root -
            self.drag_x
        )

        dy = (
            event.y_root -
            self.drag_y
        )

        x = self.start_window_x + dx
        y = self.start_window_y + dy

        self.root.geometry(
            f"+{x}+{y}"
        )

        self.pos_x = x
        self.pos_y = y

        # Save position
        self.save_settings()

    # =====================================================
    # RESIZE
    # =====================================================

    def start_resize(self, event):

        if self.locked:
            return

        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root

        self.resize_start_width = (
            self.root.winfo_width()
        )

        self.resize_start_height = (
            self.root.winfo_height()
        )

    def do_resize(self, event):

        if self.locked:
            return

        dx = (
            event.x_root -
            self.resize_start_x
        )

        dy = (
            event.y_root -
            self.resize_start_y
        )

        new_width = max(
            self.min_width,
            self.resize_start_width + dx
        )

        new_height = max(
            self.min_height,
            self.resize_start_height + dy
        )

        self.width = new_width
        self.height = new_height

        self.root.geometry(
            f"{new_width}x{new_height}"
        )

        self.save_settings()

    # =====================================================
    # SPEED FORMAT
    # =====================================================

    def format_speed(self, speed):

        if speed >= 1024 * 1024:

            return (
                f"{speed / (1024 * 1024):.2f}"
                " MB/s"
            )

        elif speed >= 1024:

            return (
                f"{speed / 1024:.0f}"
                " KB/s"
            )

        else:

            return (
                f"{speed:.0f}"
                " B/s"
            )

    # =====================================================
    # DATA FORMAT
    # =====================================================

    def format_data(self, value):

        if value >= 1024 ** 3:

            return (
                f"{value / (1024 ** 3):.2f}"
                " GB"
            )

        elif value >= 1024 ** 2:

            return (
                f"{value / (1024 ** 2):.1f}"
                " MB"
            )

        elif value >= 1024:

            return (
                f"{value / 1024:.0f}"
                " KB"
            )

        else:

            return (
                f"{value:.0f}"
                " B"
            )

    # =====================================================
    # SYSTEM STATS
    # =====================================================

    def update_stats(self):

        net = psutil.net_io_counters()

        download = (
            net.bytes_recv -
            self.old_download
        )

        upload = (
            net.bytes_sent -
            self.old_upload
        )

        # =================================================
        # DAILY DATA
        # =================================================

        # Make sure date is correct
        today = str(date.today())

        if self.data_date != today:

            self.data_date = today

            self.today_download = 0
            self.today_upload = 0

        self.today_download += max(
            0,
            download
        )

        self.today_upload += max(
            0,
            upload
        )

        self.save_daily_data()

        # =================================================
        # OLD COUNTERS
        # =================================================

        self.old_download = net.bytes_recv
        self.old_upload = net.bytes_sent

        # =================================================
        # CPU / RAM / BATTERY
        # =================================================

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        battery = psutil.sensors_battery()

        if battery:

            battery_text = (
                f"{battery.percent:.0f}%"
            )

        else:

            battery_text = "--"

        # =================================================
        # SPEED
        # =================================================

        download_text = self.format_speed(
            download
        )

        upload_text = self.format_speed(
            upload
        )

        # =================================================
        # WIDGET TEXT
        # =================================================

        text = (

            f"↓ {download_text}    "
            f"↑ {upload_text}\n"

            f"CPU {cpu:.0f}%   "
            f"RAM {ram:.0f}%   "
            f"🔋 {battery_text}"
        )

        self.label.config(
            text=text
        )

        self.root.after(
            1000,
            self.update_stats
        )

    # =====================================================
    # SHOW DATA USAGE
    # =====================================================

    def show_data_usage(self):

        total = (
            self.today_download +
            self.today_upload
        )

        # Popup
        popup = tk.Toplevel(
            self.root
        )

        popup.title(
            "Today's Data Usage"
        )

        popup.geometry(
            "300x220"
        )

        popup.resizable(
            False,
            False
        )

        popup.attributes(
            "-topmost",
            True
        )

        popup.configure(
            bg=self.background
        )

        # Title

        title = tk.Label(
            popup,

            text="📊 Today's Data Usage",

            font=(
                "Segoe UI",
                13,
                "bold"
            ),

            fg=self.text_color,
            bg=self.background
        )

        title.pack(
            pady=(15, 10)
        )

        # Download

        download_label = tk.Label(
            popup,

            text=(
                "↓ Download\n"
                + self.format_data(
                    self.today_download
                )
            ),

            font=(
                "Segoe UI",
                11,
                "bold"
            ),

            fg=self.text_color,
            bg=self.background,

            justify="left"
        )

        download_label.pack(
            anchor="w",
            padx=35,
            pady=3
        )

        # Upload

        upload_label = tk.Label(
            popup,

            text=(
                "↑ Upload\n"
                + self.format_data(
                    self.today_upload
                )
            ),

            font=(
                "Segoe UI",
                11,
                "bold"
            ),

            fg=self.text_color,
            bg=self.background,

            justify="left"
        )

        upload_label.pack(
            anchor="w",
            padx=35,
            pady=3
        )

        # Total

        total_label = tk.Label(
            popup,

            text=(
                "Total\n"
                + self.format_data(
                    total
                )
            ),

            font=(
                "Segoe UI",
                11,
                "bold"
            ),

            fg=self.accent_color,
            bg=self.background,

            justify="left"
        )

        total_label.pack(
            anchor="w",
            padx=35,
            pady=5
        )

        # Reset

        reset_button = tk.Button(
            popup,

            text="Reset Today's Data",

            command=lambda:
            self.reset_daily_data(
                popup
            )
        )

        reset_button.pack(
            pady=8
        )

    # =====================================================
    # RESET DAILY DATA
    # =====================================================

    def reset_daily_data(
        self,
        popup=None
    ):

        result = messagebox.askyesno(
            "Reset Data",
            "Reset today's download/upload data?"
        )

        if not result:
            return

        self.today_download = 0
        self.today_upload = 0

        self.data_date = str(
            date.today()
        )

        self.save_daily_data()

        if popup:

            popup.destroy()

    # =====================================================
    # MENU
    # =====================================================

    def update_menu(self):

        self.menu.delete(
            0,
            tk.END
        )

        # =================================================
        # PIN
        # =================================================

        self.menu.add_command(
            label=(
                "📌 Unpin"
                if self.pinned
                else "📌 Pin"
            ),

            command=self.toggle_pin
        )

        # =================================================
        # LOCK
        # =================================================

        self.menu.add_command(
            label=(
                "🔓 Unlock Position"
                if self.locked
                else "🔒 Lock Position"
            ),

            command=self.toggle_lock
        )

        # =================================================
        # STARTUP
        # =================================================

        self.menu.add_command(
            label=(
                "🚀 Disable Windows Startup"
                if self.startup
                else "🚀 Enable Windows Startup"
            ),

            command=self.toggle_startup
        )

        # =================================================
        # DATA USAGE
        # =================================================

        self.menu.add_command(
            label="📊 Today's Data Usage",

            command=self.show_data_usage
        )

        self.menu.add_separator()

        # =================================================
        # SIZE
        # =================================================

        size_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        size_menu.add_command(
            label="Small",

            command=lambda:
            self.set_size(
                155,
                48,
                8
            )
        )

        size_menu.add_command(
            label="Normal",

            command=lambda:
            self.set_size(
                190,
                58,
                9
            )
        )

        size_menu.add_command(
            label="Large",

            command=lambda:
            self.set_size(
                220,
                66,
                10
            )
        )

        size_menu.add_command(
            label="Extra Large",

            command=lambda:
            self.set_size(
                250,
                74,
                11
            )
        )

        self.menu.add_cascade(
            label="📏 Size",

            menu=size_menu
        )

        # =================================================
        # PADDING
        # =================================================

        padding_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        padding_menu.add_command(
            label="Compact",

            command=lambda:
            self.set_padding(
                4,
                2
            )
        )

        padding_menu.add_command(
            label="Normal",

            command=lambda:
            self.set_padding(
                8,
                4
            )
        )

        padding_menu.add_command(
            label="Wide",

            command=lambda:
            self.set_padding(
                12,
                6
            )
        )

        self.menu.add_cascade(
            label="↔ Padding",

            menu=padding_menu
        )

        # =================================================
        # COLORS
        # =================================================

        self.menu.add_command(
            label="🎨 Background Color",

            command=self.change_background
        )

        self.menu.add_command(
            label="🎨 Text Color",

            command=self.change_text_color
        )

        self.menu.add_command(
            label="✨ Accent Color",

            command=self.change_accent
        )

        # =================================================
        # TRANSPARENCY
        # =================================================

        opacity_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        for value in (
            1.0,
            0.90,
            0.80,
            0.70,
            0.60
        ):

            opacity_menu.add_command(
                label=f"{int(value * 100)}%",

                command=lambda v=value:
                self.set_opacity(v)
            )

        self.menu.add_cascade(
            label="🌫 Transparency",

            menu=opacity_menu
        )

        # =================================================
        # FONT
        # =================================================

        font_menu = tk.Menu(
            self.menu,
            tearoff=0
        )

        for size in (
            8,
            9,
            10,
            11,
            12
        ):

            font_menu.add_command(
                label=f"{size}px",

                command=lambda s=size:
                self.set_font(s)
            )

        self.menu.add_cascade(
            label="🔤 Font Size",

            menu=font_menu
        )

        self.menu.add_separator()

        # =================================================
        # EXIT
        # =================================================

        self.menu.add_command(
            label="❌ Exit",

            command=self.exit_app
        )

    # =====================================================
    # PIN
    # =====================================================

    def toggle_pin(self):

        self.pinned = not self.pinned

        self.root.attributes(
            "-topmost",
            self.pinned
        )

        self.save_settings()

        self.update_menu()

    # =====================================================
    # LOCK
    # =====================================================

    def toggle_lock(self):

        self.locked = not self.locked

        self.save_settings()

        self.update_menu()

    # =====================================================
    # WINDOWS STARTUP
    # =====================================================

    def toggle_startup(self):

        try:

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,

                r"Software\Microsoft\Windows\CurrentVersion\Run",

                0,

                winreg.KEY_SET_VALUE
            )

            if not self.startup:

                if getattr(
                    sys,
                    "frozen",
                    False
                ):

                    app_path = sys.executable

                else:

                    python_path = sys.executable

                    script_path = os.path.abspath(
                        __file__
                    )

                    app_path = (
                        f'"{python_path}" '
                        f'"{script_path}"'
                    )

                winreg.SetValueEx(
                    key,

                    STARTUP_NAME,

                    0,

                    winreg.REG_SZ,

                    app_path
                )

                self.startup = True

            else:

                try:

                    winreg.DeleteValue(
                        key,
                        STARTUP_NAME
                    )

                except FileNotFoundError:
                    pass

                self.startup = False

            winreg.CloseKey(key)

            self.save_settings()

            self.update_menu()

        except Exception as e:

            messagebox.showerror(
                "Startup Error",
                str(e)
            )

    # =====================================================
    # SIZE
    # =====================================================

    def set_size(
        self,
        width,
        height,
        font_size
    ):

        self.width = width
        self.height = height
        self.font_size = font_size

        self.root.geometry(
            f"{width}x{height}"
        )

        self.label.config(
            font=(
                "Segoe UI",
                font_size,
                "bold"
            )
        )

        self.save_settings()

    # =====================================================
    # PADDING
    # =====================================================

    def set_padding(
        self,
        x,
        y
    ):

        self.padding_x = x
        self.padding_y = y

        self.label.pack_forget()

        self.label.pack(
            fill="both",
            expand=True,
            padx=x,
            pady=y
        )

        self.save_settings()

    # =====================================================
    # FONT
    # =====================================================

    def set_font(
        self,
        size
    ):

        self.font_size = size

        self.label.config(
            font=(
                "Segoe UI",
                size,
                "bold"
            )
        )

        self.save_settings()

    # =====================================================
    # BACKGROUND COLOR
    # =====================================================

    def change_background(self):

        color = colorchooser.askcolor(
            title="Background Color"
        )[1]

        if color:

            self.background = color

            self.apply_colors()

            self.save_settings()

    # =====================================================
    # TEXT COLOR
    # =====================================================

    def change_text_color(self):

        color = colorchooser.askcolor(
            title="Text Color"
        )[1]

        if color:

            self.text_color = color

            self.apply_colors()

            self.save_settings()

    # =====================================================
    # ACCENT COLOR
    # =====================================================

    def change_accent(self):

        color = colorchooser.askcolor(
            title="Accent Color"
        )[1]

        if color:

            self.accent_color = color

            self.apply_colors()

            self.save_settings()

    # =====================================================
    # APPLY COLORS
    # =====================================================

    def apply_colors(self):

        self.root.configure(
            bg=self.background
        )

        self.frame.configure(
            bg=self.background,
            highlightbackground=self.accent_color
        )

        self.label.configure(
            bg=self.background,
            fg=self.text_color
        )

        self.resize_handle.configure(
            bg=self.background,
            fg=self.accent_color
        )

    # =====================================================
    # OPACITY
    # =====================================================

    def set_opacity(
        self,
        value
    ):

        self.opacity = value

        self.root.attributes(
            "-alpha",
            value
        )

        self.save_settings()

    # =====================================================
    # RIGHT CLICK
    # =====================================================

    def show_menu(
        self,
        event
    ):

        try:

            self.menu.tk_popup(
                event.x_root,
                event.y_root
            )

        finally:

            self.menu.grab_release()

    # =====================================================
    # EXIT
    # =====================================================

    def exit_app(self):

        self.save_settings()

        self.root.destroy()


# =========================================================
# START APP
# =========================================================

root = tk.Tk()

app = MaterialGlassSpeedMeter(
    root
)

root.mainloop()