# tools/db54_tk.py
import threading
import time
import tkinter as tk
from tkinter import font, messagebox, ttk

import snap7
from snap7 import util

# ---------- Config DB54 ----------
DEFAULT_PLC_IP = "192.168.190.53"
RACK = 0
SLOT = 1

DB_NUMBER = 54
START_ADDRESS = 0
SIZE = 94  # ครอบคลุม offset 92 + 2 bytes

# Data Layout (INT16 ทุกช่อง)
DB_TAGS = [
    {"label": "Brightness", "desc": "ความสว่างจอ", "offset": 0},
    {"label": "P1_COLLER", "desc": "สีข้อความที่ 1", "offset": 2},
    {"label": "P1_TEXT", "desc": "ข้อความที่ 1", "offset": 4},
    {"label": "P2_COLLER", "desc": "สีข้อความที่ 2", "offset": 6},
    {"label": "P2_TEXT", "desc": "ข้อความที่ 2", "offset": 8},
    {"label": "P3_COLLER", "desc": "สีข้อความที่ 3", "offset": 10},
    {"label": "P3_TEXT", "desc": "ข้อความที่ 3", "offset": 12},
    {"label": "P4_COLLER", "desc": "สีข้อความที่ 4", "offset": 14},
    {"label": "P4_TEXT", "desc": "ข้อความที่ 4", "offset": 16},
    {"label": "P5_COLLER", "desc": "สีข้อความที่ 5", "offset": 18},
    {"label": "P5_TEXT", "desc": "ข้อความที่ 5", "offset": 20},
    {"label": "P6_COLLER", "desc": "สีข้อความที่ 6", "offset": 22},
    {"label": "P6_TEXT", "desc": "ข้อความที่ 6", "offset": 24},
    {"label": "P7_COLLER", "desc": "สีข้อความที่ 7", "offset": 26},
    {"label": "P7_TEXT", "desc": "ข้อความที่ 7", "offset": 28},
    {"label": "P8_COLLER", "desc": "สีข้อความที่ 8", "offset": 30},
    {"label": "P8_TEXT", "desc": "ข้อความที่ 8", "offset": 32},
    {"label": "P9_COLLER", "desc": "สีข้อความที่ 9", "offset": 34},
    {"label": "P9_TEXT", "desc": "ข้อความที่ 9", "offset": 36},
    {"label": "P10_COLLER", "desc": "สีข้อความที่ 10", "offset": 38},
    {"label": "P10_TEXT", "desc": "ข้อความที่ 10", "offset": 40},
    {"label": "P11_COLLER", "desc": "สีข้อความที่ 11", "offset": 42},
    {"label": "P11_TEXT", "desc": "ข้อความที่ 11", "offset": 44},
    {"label": "P12_COLLER", "desc": "สีข้อความที่ 12", "offset": 46},
    {"label": "P12_TEXT", "desc": "ข้อความที่ 12", "offset": 48},
    {"label": "P13_COLLER", "desc": "สีข้อความที่ 13", "offset": 50},
    {"label": "P13_TEXT", "desc": "ข้อความที่ 13", "offset": 52},
    {"label": "P14_COLLER", "desc": "สีข้อความที่ 14", "offset": 54},
    {"label": "P14_TEXT", "desc": "ข้อความที่ 14", "offset": 56},
    {"label": "P15_COLLER", "desc": "สีข้อความที่ 15", "offset": 58},
    {"label": "P15_TEXT", "desc": "ข้อความที่ 15", "offset": 60},
    {"label": "P16_COLLER", "desc": "สีข้อความที่ 16", "offset": 62},
    {"label": "P16_TEXT", "desc": "ข้อความที่ 16", "offset": 64},
    {"label": "P17_COLLER", "desc": "สีข้อความที่ 17", "offset": 66},
    {"label": "P17_TEXT", "desc": "ข้อความที่ 17", "offset": 68},
    {"label": "P18_COLLER", "desc": "สีข้อความที่ 18", "offset": 70},
    {"label": "P18_TEXT", "desc": "ข้อความที่ 18", "offset": 72},
    {"label": "P19_COLLER", "desc": "สีข้อความที่ 19", "offset": 74},
    {"label": "P19_TEXT", "desc": "ข้อความที่ 19", "offset": 76},
    {"label": "P20_COLLER", "desc": "สีข้อความที่ 20", "offset": 78},
    {"label": "P20_TEXT", "desc": "ข้อความที่ 20", "offset": 80},
    {"label": "P21_COLLER", "desc": "สีข้อความที่ 21", "offset": 82},
    {"label": "P21_TEXT", "desc": "ข้อความที่ 21", "offset": 84},
    {"label": "P22_COLLER", "desc": "สีข้อความที่ 22", "offset": 86},
    {"label": "P22_TEXT", "desc": "ข้อความที่ 22", "offset": 88},
    {"label": "P23_COLLER", "desc": "สีข้อความที่ 23", "offset": 90},
    {"label": "P23_TEXT", "desc": "ข้อความที่ 23", "offset": 92},
]

# Marker: M150.0
M_BASE_SENT_DATA = 150
M_SENT_DATA_BIT = 0

# แผนที่ “ชื่อล้วน” <-> ค่าเลข (สำหรับ Combobox)
BRIGHTNESS_VALUE_TO_DISPLAY = {
    "0": "0%",
    "1": "25%",
    "2": "50%",
    "3": "75%",
    "4": "100%",
}
COLOR_VALUE_TO_DISPLAY = {
    "0": "แดง",
    "1": "เหลือง",
    "2": "เขียว",
    "3": "ฟ้า",
    "4": "น้ำเงิน",
    "5": "ชมพู",
}
TEXT_VALUE_TO_DISPLAY = {"0": "EUDR", "1": "FSC", "2": "REG"}

BRIGHTNESS_DISPLAY_TO_VALUE = {v: k for k, v in BRIGHTNESS_VALUE_TO_DISPLAY.items()}
COLOR_DISPLAY_TO_VALUE = {v: k for k, v in COLOR_VALUE_TO_DISPLAY.items()}
TEXT_DISPLAY_TO_VALUE = {v: k for k, v in TEXT_VALUE_TO_DISPLAY.items()}

# Extra reads P1..P23 (จาก DB3..DB25, DBW18)
EXTRA_READS_CONFIG = [
    {"label": f"P{i}", "db": i + 3 - 2, "addr": 18, "size": 2} for i in range(1, 24)
]


class PlcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PLC Control Panel (DB54)")
        self.root.geometry("740x820")
        self.root.resizable(True, True)
        self.root.minsize(680, 760)

        self.client = snap7.client.Client()
        self.is_connected = False
        self.is_running = True
        self._lock = threading.Lock()

        self.entry_vars = []
        self.entry_widgets = []
        self.entry_types = []
        self.extra_read_vars = {}

        self._configure_styles()
        self._build_ui()

        self.read_thread = threading.Thread(target=self._periodic_read, daemon=True)
        self.read_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI / Styles ----------
    def _configure_styles(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.default_font = font.Font(family="Segoe UI", size=11)
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.status_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=11, weight="bold")

        BG = "#f0f2f5"
        self.FRAME_BG = "#ffffff"
        TXT = "#2f2f2f"
        PRIMARY = "#0078d4"
        self.OK = "#107c10"
        self.ERR = "#d83b01"

        self.root.configure(background=BG)
        self.style.configure(".", font=self.default_font, background=BG, foreground=TXT)
        self.style.configure("TFrame", background=self.FRAME_BG)
        self.style.configure(
            "TLabelframe", background=self.FRAME_BG, borderwidth=1, relief="solid"
        )
        self.style.configure(
            "TLabelframe.Label",
            font=self.title_font,
            background=self.FRAME_BG,
            foreground=PRIMARY,
        )
        self.style.configure("TButton", font=self.button_font, padding=(12, 8))
        self.style.configure("Accent.TButton", foreground="white", background=PRIMARY)
        self.style.configure(
            "TEntry",
            fieldbackground="white",
            font=font.Font(family="Segoe UI", size=12),
        )
        self.style.configure("TCombobox", font=font.Font(family="Segoe UI", size=12))

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        # Status
        fr_status = ttk.LabelFrame(main, text="PLC Status", padding=15)
        fr_status.pack(fill="x", pady=(0, 10))
        fr_status.columnconfigure(1, weight=1)

        ttk.Label(fr_status, text="IP Address:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.entry_ip = ttk.Entry(fr_status, width=20)
        self.entry_ip.grid(row=0, column=1, sticky="ew", pady=5)
        self.entry_ip.insert(0, DEFAULT_PLC_IP)

        btns = ttk.Frame(fr_status, style="TFrame")
        btns.grid(row=0, column=2, sticky="e", padx=(20, 0))
        self.btn_connect = ttk.Button(btns, text="Connect", command=self.connect_plc)
        self.btn_connect.pack(side="left")
        self.btn_disconnect = ttk.Button(
            btns, text="Disconnect", command=self.disconnect_plc, state="disabled"
        )
        self.btn_disconnect.pack(side="left", padx=(5, 0))

        ttk.Label(fr_status, text="Connection:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.lbl_status = ttk.Label(
            fr_status, text="DISCONNECTED", font=self.status_font, foreground=self.ERR
        )
        self.lbl_status.grid(row=1, column=1, sticky="w")

        ttk.Label(fr_status, text="SENT DATA (%M150.0):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.lbl_sent = ttk.Label(
            fr_status, text="OFF", font=self.status_font, foreground="#777"
        )
        self.lbl_sent.grid(row=2, column=1, sticky="w")

        ttk.Separator(fr_status).grid(
            row=3, column=0, columnspan=3, sticky="ew", pady=10
        )

        # P1..P23 (3 คอลัมน์) ในพื้นที่เลื่อน
        p_container = ttk.Frame(fr_status, height=260)
        p_container.grid(row=4, column=0, columnspan=3, sticky="nsew")
        p_container.pack_propagate(False)

        canvas_p = tk.Canvas(
            p_container, background=self.FRAME_BG, highlightthickness=0
        )
        vsb_p = ttk.Scrollbar(p_container, orient="vertical", command=canvas_p.yview)
        frm_p = ttk.Frame(canvas_p, style="TFrame")
        frm_p.bind(
            "<Configure>",
            lambda e: canvas_p.configure(scrollregion=canvas_p.bbox("all")),
        )
        canvas_p.create_window((0, 0), window=frm_p, anchor="nw")
        canvas_p.configure(yscrollcommand=vsb_p.set)
        canvas_p.pack(side="left", fill="both", expand=True)
        vsb_p.pack(side="right", fill="y")

        self.extra_read_vars.clear()
        cols = 3
        for i, cfg in enumerate(EXTRA_READS_CONFIG):
            r = i // cols
            c = (i % cols) * 2
            ttk.Label(
                frm_p, text=f"{cfg['label']} (DB{cfg['db']}.DBW{cfg['addr']}):"
            ).grid(row=r, column=c, sticky="w", padx=(20 if c else 10, 5), pady=3)
            var = tk.StringVar(value="---")
            ttk.Label(
                frm_p, textvariable=var, font=self.status_font, foreground="#0078d4"
            ).grid(row=r, column=c + 1, sticky="w", padx=(0, 12), pady=3)
            self.extra_read_vars[cfg["label"]] = var

        # DB54 Editor
        fr_db = ttk.LabelFrame(main, text="Data Center (DB54)", padding=10)
        fr_db.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(fr_db, background=self.FRAME_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(fr_db, orient="vertical", command=canvas.yview)
        self.frm_scroll = ttk.Frame(canvas, style="TFrame")
        self.frm_scroll.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.frm_scroll, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vsb.pack(side="right", fill="y")

        # Actions
        actions = ttk.Frame(self.frm_scroll, padding=(10, 10, 10, 12))
        actions.grid(row=0, column=0, columnspan=3, sticky="ew")
        actions.columnconfigure((0, 1), weight=1)

        self.btn_write_and_pulse = ttk.Button(
            actions,
            text="Write & Pulse",
            command=self._write_and_pulse_thread,
            style="Accent.TButton",
            state="disabled",
        )
        self.btn_write_and_pulse.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.btn_reload = ttk.Button(
            actions,
            text="Reload from DB",
            command=self.read_db_to_gui,
            state="disabled",
        )
        self.btn_reload.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.frm_scroll.columnconfigure(2, weight=1)

        # สร้าง Combobox “ชื่อล้วน”
        self.entry_vars.clear(), self.entry_widgets.clear(), self.entry_types.clear()
        for i, tag in enumerate(DB_TAGS):
            row = i + 1
            ttk.Label(self.frm_scroll, text=tag["label"], width=15).grid(
                row=row, column=0, sticky="w", padx=(10, 10), pady=8
            )
            ttk.Label(self.frm_scroll, text=tag["desc"], width=22).grid(
                row=row, column=1, sticky="w", padx=(0, 20), pady=8
            )

            if "Brightness" in tag["label"]:
                options = list(BRIGHTNESS_VALUE_TO_DISPLAY.values())
                ttype = "brightness"
            elif "_COLLER" in tag["label"]:
                options = list(COLOR_VALUE_TO_DISPLAY.values())
                ttype = "color"
            elif "_TEXT" in tag["label"]:
                options = list(TEXT_VALUE_TO_DISPLAY.values())
                ttype = "text"
            else:
                options, ttype = ["0"], "raw"

            var = tk.StringVar()
            cmb = ttk.Combobox(
                self.frm_scroll,
                textvariable=var,
                values=options,
                state="readonly",
                width=20,
            )
            cmb.grid(row=row, column=2, sticky="w", padx=(0, 10), pady=8)

            self.entry_vars.append(var)
            self.entry_widgets.append(cmb)
            self.entry_types.append(ttype)

    # ---------- PLC Ops ----------
    def connect_plc(self):
        ip = self.entry_ip.get().strip()
        if not ip:
            messagebox.showwarning("Input Error", "Please enter the PLC IP Address.")
            return
        try:
            with self._lock:
                self.client.connect(ip, RACK, SLOT)
                self.is_connected = True
            self._ui_connected(True)
            self.read_db_to_gui()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to PLC:\n{e}")

    def disconnect_plc(self):
        try:
            with self._lock:
                if self.is_connected:
                    self.client.disconnect()
            self.is_connected = False
        finally:
            self._ui_connected(False)

    def _ui_connected(self, ok: bool):
        state = "normal" if ok else "disabled"
        self.lbl_status.config(
            text="CONNECTED" if ok else "DISCONNECTED",
            foreground=self.OK if ok else self.ERR,
        )
        self.entry_ip.config(state="disabled" if ok else "normal")
        self.btn_connect.config(state="disabled" if ok else "normal")
        self.btn_disconnect.config(state=state)
        self.btn_write_and_pulse.config(state=state)
        self.btn_reload.config(state=state)
        if not ok:
            self.lbl_sent.config(text="OFF", foreground="#777")

    def _periodic_read(self):
        while self.is_running:
            sent = False
            extra = {}
            if self.is_connected:
                try:
                    with self._lock:
                        b = self.client.mb_read(M_BASE_SENT_DATA, 1)
                        sent = util.get_bool(b, 0, M_SENT_DATA_BIT)
                    for cfg in EXTRA_READS_CONFIG:
                        with self._lock:
                            raw = self.client.db_read(
                                cfg["db"], cfg["addr"], cfg["size"]
                            )
                        extra[cfg["label"]] = int(util.get_int(raw, 0))
                    self.root.after(0, self._update_periodic_gui, sent, extra)
                except Exception:
                    self.root.after(0, self.disconnect_plc)
            time.sleep(0.5)

    def _update_periodic_gui(self, sent, extra_values):
        self.lbl_sent.config(
            text="ON" if sent else "OFF", foreground=self.OK if sent else "#777"
        )
        for k, var in self.extra_read_vars.items():
            var.set(str(extra_values.get(k, "---")))

    def read_db_to_gui(self):
        if not self.is_connected:
            return
        try:
            with self._lock:
                data = self.client.db_read(DB_NUMBER, START_ADDRESS, SIZE)

            vals = []
            for tag in DB_TAGS:
                off = tag["offset"] - START_ADDRESS
                vals.append(util.get_int(data, off))

            def fill():
                for i, v in enumerate(vals):
                    widget, var, ttype = (
                        self.entry_widgets[i],
                        self.entry_vars[i],
                        self.entry_types[i],
                    )
                    if ttype == "brightness":
                        txt = BRIGHTNESS_VALUE_TO_DISPLAY.get(str(v), str(v))
                    elif ttype == "color":
                        txt = COLOR_VALUE_TO_DISPLAY.get(str(v), str(v))
                    elif ttype == "text":
                        txt = TEXT_VALUE_TO_DISPLAY.get(str(v), str(v))
                    else:
                        txt = str(v)
                    if self.root.focus_get() != widget:
                        var.set(txt)

            self.root.after(0, fill)
        except Exception as e:
            print("Read DB54 Error:", e)
            self.disconnect_plc()

    def _write_and_pulse_thread(self):
        threading.Thread(target=self._write_and_pulse, daemon=True).start()

    def _write_and_pulse(self):
        if not self.is_connected:
            return
        try:
            self.root.after(
                0, lambda: self.btn_write_and_pulse.config(state="disabled")
            )
            self.root.after(0, lambda: self.btn_reload.config(state="disabled"))

            # collect selections -> number
            values = []
            for i, var in enumerate(self.entry_vars):
                sel = var.get().strip()
                ttype = self.entry_types[i]
                if ttype == "brightness":
                    num = BRIGHTNESS_DISPLAY_TO_VALUE.get(sel, sel)
                elif ttype == "color":
                    num = COLOR_DISPLAY_TO_VALUE.get(sel, sel)
                elif ttype == "text":
                    num = TEXT_DISPLAY_TO_VALUE.get(sel, sel)
                else:
                    num = sel or "0"
                values.append(int(num))

            with self._lock:
                buf = bytearray(self.client.db_read(DB_NUMBER, START_ADDRESS, SIZE))
            for i, v in enumerate(values):
                off = DB_TAGS[i]["offset"] - START_ADDRESS
                util.set_int(buf, off, v)
            with self._lock:
                self.client.db_write(DB_NUMBER, START_ADDRESS, buf)

            # Pulse M150.0 ~0.5s
            with self._lock:
                m = self.client.mb_read(M_BASE_SENT_DATA, 1)
            util.set_bool(m, 0, M_SENT_DATA_BIT, True)
            with self._lock:
                self.client.mb_write(M_BASE_SENT_DATA, 1, m)
            time.sleep(0.5)
            with self._lock:
                m2 = self.client.mb_read(M_BASE_SENT_DATA, 1)
            util.set_bool(m2, 0, M_SENT_DATA_BIT, False)
            with self._lock:
                self.client.mb_write(M_BASE_SENT_DATA, 1, m2)

            self.root.after(
                0,
                lambda: messagebox.showinfo("Success", "Wrote DB54 and pulsed %M150.0"),
            )
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"{e}"))
        finally:
            if self.is_connected:
                self.root.after(
                    0, lambda: self.btn_write_and_pulse.config(state="normal")
                )
                self.root.after(0, lambda: self.btn_reload.config(state="normal"))

    def on_close(self):
        self.is_running = False
        time.sleep(0.1)
        self.disconnect_plc()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlcApp(root)
    root.mainloop()
