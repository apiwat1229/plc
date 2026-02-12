import threading
import time
import tkinter as tk
from tkinter import font, messagebox, ttk

import snap7
from snap7 import util

# ---------- Config (แก้ไขตาม image_cacb79.png) ----------
DEFAULT_PLC_IP = "192.168.190.51"  # ✅ Updated IP
RACK = 0
SLOT = 1

DB_NUMBER = 26

# ✅ Updated: กำหนดโครงสร้าง DB Tag ตามรูป
# (Name, Description, DB Offset)
DB_TAGS = [
    {"label": "Data_Center[1]", "desc": "หมายเลขบ่อ บรรทัดที่ 1", "offset": 2},
    {"label": "Data_Center[3]", "desc": "จำนวนตัก บรรทัดที่ 1", "offset": 6},
    {"label": "Data_Center[5]", "desc": "หมายเลขบ่อ บรรทัดที่ 2", "offset": 10},
    {"label": "Data_Center[7]", "desc": "จำนวนตัก บรรทัดที่ 2", "offset": 14},
    {"label": "Data_Center[9]", "desc": "หมายเลขบ่อ บรรทัดที่ 3", "offset": 18},
    {"label": "Data_Center[11]", "desc": "จำนวนตัก บรรทัดที่ 3", "offset": 22},
    {"label": "Data_Center[13]", "desc": "หมายเลขบ่อ บรรทัดที่ 4", "offset": 26},
    {"label": "Data_Center[15]", "desc": "จำนวนตัก บรรทัดที่ 4", "offset": 30},
]

# ✅ Updated: กำหนด Address และขนาดที่จะอ่าน/เขียน
# อ่านตั้งแต่ offset 0 ขนาด 32 bytes (จะครอบคลุม DBW30 ซึ่งอยู่ที่ byte 30, 31)
START_ADDRESS = 0
SIZE = 32  # ขนาด (32 bytes) เพียงพอที่จะครอบคลุม offset 30 + 2 bytes (int)

# Markers (ตาม Ladder และรูป)
M_BASE_LINE_USE = 10  # ✅ Added: M-Base สำหรับ Line Use
M_BASE_SENT_DATA = 150  # (M150.0)

M_SENT_DATA_BIT = 0  # (%M150.0)
M_LINE1_USE_BIT = 0  # (%M10.0) ✅ Added
M_LINE2_USE_BIT = 1  # (%M10.1) ✅ Added
M_LINE3_USE_BIT = 2  # (%M10.2) ✅ Added
M_LINE4_USE_BIT = 3  # (%M10.3) ✅ Added

# ✅ Removed M_INT_SENT_BIT และ INT_SENT_HOLD_SECONDS


class PlcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PLC Control Panel (Fixed)")
        self.root.geometry("650x750")  # ✅ Adjusted height
        self.root.resizable(False, False)

        self.client = snap7.client.Client()
        self.is_connected = False
        self.is_running = True
        self._lock = threading.Lock()
        
        # ✅ Added: ตัวแปรสำหรับ Checkbuttons
        self.line1_use_var = tk.BooleanVar(value=False)
        self.line2_use_var = tk.BooleanVar(value=False)
        self.line3_use_var = tk.BooleanVar(value=False)
        self.line4_use_var = tk.BooleanVar(value=False)
        
        self.line_use_checks = [] # ✅ Added: List ไว้เก็บ Checkbuttons

        self._configure_styles()
        self._build_ui()

        self.read_thread = threading.Thread(target=self._periodic_read, daemon=True)
        self.read_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_styles(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        # Fonts
        self.default_font = font.Font(family="Segoe UI", size=11)
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.status_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=11, weight="bold")

        # Colors
        BG_COLOR = "#f0f2f5"
        self.FRAME_BG = "#ffffff"
        TEXT_COLOR = "#2f2f2f"
        PRIMARY_COLOR = "#0078d4"
        SUCCESS_COLOR = "#107c10"
        ERROR_COLOR = "#d83b01"

        self.root.configure(background=BG_COLOR)

        self.style.configure(
            ".", font=self.default_font, background=BG_COLOR, foreground=TEXT_COLOR
        )
        self.style.configure("TFrame", background=self.FRAME_BG)
        self.style.configure(
            "TLabelframe", background=self.FRAME_BG, borderwidth=1, relief="solid"
        )
        self.style.configure(
            "TLabelframe.Label",
            font=self.title_font,
            background=self.FRAME_BG,
            foreground=PRIMARY_COLOR,
        )
        self.style.configure(
            "TButton",
            font=self.button_font,
            padding=(12, 8),
            borderwidth=1,
            relief="solid",
        )
        self.style.map(
            "TButton",
            foreground=[("disabled", "#a0a0a0"), ("!disabled", TEXT_COLOR)],
            background=[("active", "#e0e0e0"), ("!disabled", "#fdfdfd")],
            bordercolor=[("!disabled", "#cccccc")],
        )
        self.style.configure(
            "Accent.TButton",
            foreground="white",
            background=PRIMARY_COLOR,
            bordercolor=PRIMARY_COLOR,
        )
        self.style.map("Accent.TButton", background=[("active", "#005a9e")])
        self.style.configure(
            "TEntry",
            fieldbackground="white",
            font=font.Font(family="Segoe UI", size=12),
        )
        # ✅ Added: Style สำหรับ Checkbutton ใน Frame
        self.style.configure("Status.TCheckbutton", background=self.FRAME_BG)
        
        self.status_colors = {"connected": SUCCESS_COLOR, "disconnected": ERROR_COLOR}

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        fr_status = ttk.LabelFrame(main_frame, text="PLC Status", padding=15)
        fr_status.pack(fill="x", pady=(0, 10))
        fr_status.columnconfigure(1, weight=1)
        fr_status.columnconfigure(3, weight=1) # ✅ Added for new markers

        ttk.Label(fr_status, text="IP Address:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.entry_ip = ttk.Entry(fr_status, width=20)
        self.entry_ip.grid(row=0, column=1, sticky="ew", pady=5)
        self.entry_ip.insert(0, DEFAULT_PLC_IP)

        btn_frame = ttk.Frame(fr_status, style="TFrame")
        btn_frame.grid(row=0, column=2, columnspan=2, sticky="e", padx=(20, 0))
        self.btn_connect = ttk.Button(
            btn_frame, text="Connect", command=self.connect_plc
        )
        self.btn_connect.pack(side="left")
        self.btn_disconnect = ttk.Button(
            btn_frame, text="Disconnect", command=self.disconnect_plc, state="disabled"
        )
        self.btn_disconnect.pack(side="left", padx=(5, 0))

        ttk.Label(fr_status, text="Connection:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.lbl_status = ttk.Label(
            fr_status,
            text="DISCONNECTED",
            font=self.status_font,
            foreground=self.status_colors["disconnected"],
        )
        self.lbl_status.grid(row=1, column=1, sticky="w")
        
        # --- ✅ Markers Updated ---
        ttk.Label(fr_status, text="SENT DATA (%M150.0):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.lbl_sent_data = ttk.Label(
            fr_status, text="OFF", font=self.status_font, foreground="#777"
        )
        self.lbl_sent_data.grid(row=2, column=1, sticky="w")
        
        # ✅ Changed: เปลี่ยน Label เป็น Checkbutton
        
        # --- LINE 1 ---
        self.chk_line1_use = ttk.Checkbutton(
            fr_status,
            text="LINE1 USE (%M10.0):",
            variable=self.line1_use_var,
            command=lambda: self._write_line_use_bit_thread(M_LINE1_USE_BIT, self.line1_use_var.get()),
            style="Status.TCheckbutton",
            state="disabled"
        )
        self.chk_line1_use.grid(row=1, column=2, sticky="w", padx=(20, 10), pady=2)
        
        # --- LINE 2 ---
        self.chk_line2_use = ttk.Checkbutton(
            fr_status,
            text="LINE2 USE (%M10.1):",
            variable=self.line2_use_var,
            command=lambda: self._write_line_use_bit_thread(M_LINE2_USE_BIT, self.line2_use_var.get()),
            style="Status.TCheckbutton",
            state="disabled"
        )
        self.chk_line2_use.grid(row=2, column=2, sticky="w", padx=(20, 10), pady=2)

        # --- LINE 3 ---
        self.chk_line3_use = ttk.Checkbutton(
            fr_status,
            text="LINE3 USE (%M10.2):",
            variable=self.line3_use_var,
            command=lambda: self._write_line_use_bit_thread(M_LINE3_USE_BIT, self.line3_use_var.get()),
            style="Status.TCheckbutton",
            state="disabled"
        )
        self.chk_line3_use.grid(row=3, column=2, sticky="w", padx=(20, 10), pady=2)
        
        # --- LINE 4 ---
        self.chk_line4_use = ttk.Checkbutton(
            fr_status,
            text="LINE4 USE (%M10.3):",
            variable=self.line4_use_var,
            command=lambda: self._write_line_use_bit_thread(M_LINE4_USE_BIT, self.line4_use_var.get()),
            style="Status.TCheckbutton",
            state="disabled"
        )
        self.chk_line4_use.grid(row=4, column=2, sticky="w", padx=(20, 10), pady=2)

        # ✅ Added: เพิ่ม Checkbuttons ลงใน List เพื่อให้จัดการ state ง่าย
        self.line_use_checks = [
            self.chk_line1_use,
            self.chk_line2_use,
            self.chk_line3_use,
            self.chk_line4_use,
        ]
        # --- End Markers ---

        fr_db = ttk.LabelFrame(main_frame, text="Data Center (DB26)", padding=10)
        fr_db.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(fr_db, background=self.FRAME_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(fr_db, orient="vertical", command=canvas.yview)
        self.frm_scroll = ttk.Frame(canvas, style="TFrame")
        self.frm_scroll.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # ✅ Updated: ปรับความกว้าง canvas
        canvas.create_window((0, 0), window=self.frm_scroll, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vsb.pack(side="right", fill="y")
        
        self.frm_scroll.columnconfigure(2, weight=1) # ✅ Allow entry to expand

        # ✅ Updated: สร้าง GUI จาก DB_TAGS
        self.entry_widgets = []
        for i, tag_info in enumerate(DB_TAGS):
            lbl_tag = ttk.Label(self.frm_scroll, text=tag_info['label'], width=15)
            lbl_tag.grid(row=i, column=0, sticky="w", padx=(10, 10), pady=8)
            
            lbl_desc = ttk.Label(self.frm_scroll, text=tag_info['desc'], width=20)
            lbl_desc.grid(row=i, column=1, sticky="w", padx=(0, 20), pady=8)
            
            ent = ttk.Entry(self.frm_scroll, width=25)
            ent.grid(row=i, column=2, sticky="ew", padx=(0, 10), pady=8)
            
            self.entry_widgets.append(ent)

        fr_actions = ttk.LabelFrame(main_frame, text="Actions", padding=15)
        fr_actions.pack(fill="x", pady=(10, 0))
        fr_actions.columnconfigure((0, 1, 2, 3), weight=1)

        # ✅ Changed: สร้างปุ่มใหม่ "Write & Pulse"
        self.btn_write_and_pulse = ttk.Button(
            fr_actions,
            text="Write & Pulse",
            command=self._write_and_pulse_thread, # ✅ Changed: command
            style="Accent.TButton",
            state="disabled",
        )
        self.btn_write_and_pulse.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 5))
        
        self.btn_reload = ttk.Button(
            fr_actions,
            text="Reload from DB",
            command=self.read_db_to_gui,
            state="disabled",
        )
        self.btn_reload.grid(row=0, column=2, columnspan=2, sticky="ew", padx=(5, 0))
        
        # ✅ Removed: btn_write และ btn_pulse_sent_data

    def connect_plc(self):
        plc_ip = self.entry_ip.get().strip()
        if not plc_ip:
            messagebox.showwarning("Input Error", "Please enter the PLC IP Address.")
            return
        try:
            with self._lock:
                self.client.connect(plc_ip, RACK, SLOT)
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
        except Exception:
            pass
        self._ui_connected(False)

    def _ui_connected(self, is_now_connected: bool):
        state = "normal" if is_now_connected else "disabled"
        self.lbl_status.config(
            text="CONNECTED" if is_now_connected else "DISCONNECTED",
            foreground=(
                self.status_colors["connected"]
                if is_now_connected
                else self.status_colors["disconnected"]
            ),
        )
        self.entry_ip.config(state="disabled" if is_now_connected else "normal")
        self.btn_connect.config(state="disabled" if is_now_connected else "normal")
        self.btn_disconnect.config(state=state)
        
        # ✅ Changed: อัปเดตปุ่มใหม่
        self.btn_write_and_pulse.config(state=state)
        self.btn_reload.config(state=state)
        # ✅ Removed: btn_write, btn_pulse_sent_data
        
        # ✅ Added: อัปเดต state ของ Checkbuttons
        for chk in self.line_use_checks:
            chk.config(state=state)
        
        if not is_now_connected:
            self._update_marker_labels(False, False, False, False, False) # ✅ Updated

    def _periodic_read(self):
        # ✅ Updated: อ่าน markers จาก 2 address (MB10, MB150)
        while self.is_running:
            if self.is_connected:
                try:
                    with self._lock:
                        buf_line_use = self.client.mb_read(M_BASE_LINE_USE, 1)
                        buf_sent_data = self.client.mb_read(M_BASE_SENT_DATA, 1)
                    
                    m_10_0 = util.get_bool(buf_line_use, 0, M_LINE1_USE_BIT)
                    m_10_1 = util.get_bool(buf_line_use, 0, M_LINE2_USE_BIT)
                    m_10_2 = util.get_bool(buf_line_use, 0, M_LINE3_USE_BIT)
                    m_10_3 = util.get_bool(buf_line_use, 0, M_LINE4_USE_BIT)
                    m_150_0 = util.get_bool(buf_sent_data, 0, M_SENT_DATA_BIT)
                    
                    self.root.after(0, self._update_marker_labels, m_10_0, m_10_1, m_10_2, m_10_3, m_150_0)
                except Exception:
                    self.root.after(0, self.disconnect_plc)
            time.sleep(0.5)

    def _update_marker_labels(self, m10_0, m10_1, m10_2, m10_3, m150_0):
        # ✅ Updated: อัปเดต Label (SENT DATA) และ BooleanVar (LINE USE)
        self.lbl_sent_data.config(
            text="ON" if m150_0 else "OFF",
            foreground=self.status_colors["connected"] if m150_0 else "#777",
        )
        
        # ✅ Changed: อัปเดต Var ของ Checkbutton (UI จะอัปเดตตาม)
        self.line1_use_var.set(m10_0)
        self.line2_use_var.set(m10_1)
        self.line3_use_var.set(m10_2)
        self.line4_use_var.set(m10_3)

    def read_db_to_gui(self):
        if not self.is_connected:
            return
        try:
            with self._lock:
                # อ่านบล็อกข้อมูล (0-32 bytes)
                data = self.client.db_read(DB_NUMBER, START_ADDRESS, SIZE)
            
            # ✅ Updated: ดึงค่าจาก offset ที่ถูกต้อง
            vals = []
            for tag_info in DB_TAGS:
                # offset ใน buffer = offset ของ tag - start address ที่เราอ่าน
                offset_in_buffer = tag_info['offset'] - START_ADDRESS
                val = util.get_int(data, offset_in_buffer)
                vals.append(val)

            def fill_gui():
                for i, v in enumerate(vals):
                    entry = self.entry_widgets[i]
                    if self.root.focus_get() != entry:
                        entry.delete(0, tk.END)
                        entry.insert(0, str(v))

            self.root.after(0, fill_gui)
        except Exception as e:
            print(f"Read DB Error: {e}")
            self.disconnect_plc()

    # ✅ Removed: write_gui_to_db(self)

    # ✅ Added: ฟังก์ชันใหม่สำหรับ Thread
    def _write_and_pulse_thread(self):
        """
        Starts the write and pulse sequence in a separate thread 
        to avoid blocking the GUI.
        """
        threading.Thread(target=self._write_and_pulse, daemon=True).start()

    # ✅ Added: ฟังก์ชันหลักที่รวม Write และ Pulse
    def _write_and_pulse(self):
        """
        Runs the Write-to-DB logic first, and if successful,
        runs the Pulse-SENT-DATA logic.
        Shows one success/error message at the end.
        """
        if not self.is_connected:
            return
        
        try:
            # 0. Disable buttons
            self.root.after(0, lambda: self.btn_write_and_pulse.config(state="disabled"))
            self.root.after(0, lambda: self.btn_reload.config(state="disabled"))

            # 1. Write to DB Logic
            # 1a. ดึงค่าจาก GUI และตรวจสอบ
            vals = []
            for i, ent in enumerate(self.entry_widgets):
                txt = ent.get().strip() or "0"
                try:
                    v = int(txt)
                except ValueError:
                    raise ValueError(
                        f"{DB_TAGS[i]['label']}: Value must be an integer (got '{txt}')"
                    )
                if not -32768 <= v <= 32767:
                    raise ValueError(
                        f"{DB_TAGS[i]['label']}: Value must be between -32768 and 32767"
                    )
                vals.append(v)

            # 1b. Read-Modify-Write
            with self._lock:
                data = self.client.db_read(DB_NUMBER, START_ADDRESS, SIZE)
            
            data = bytearray(data) # แปลงเป็น bytearray เพื่อให้แก้ไขได้

            for i, v in enumerate(vals):
                tag_info = DB_TAGS[i]
                offset_in_buffer = tag_info['offset'] - START_ADDRESS
                util.set_int(data, offset_in_buffer, v)

            with self._lock:
                self.client.db_write(DB_NUMBER, START_ADDRESS, data)
                
            # --- Write OK ---

            # 2. Pulse Logic
            with self._lock:
                buf = self.client.mb_read(M_BASE_SENT_DATA, 1)
            
            util.set_bool(buf, 0, M_SENT_DATA_BIT, True)
            with self._lock:
                self.client.mb_write(M_BASE_SENT_DATA, 1, buf)
            
            time.sleep(0.5) # This is why we need a thread
            
            with self._lock:
                buf2 = self.client.mb_read(M_BASE_SENT_DATA, 1)
            
            util.set_bool(buf2, 0, M_SENT_DATA_BIT, False)
            with self._lock:
                self.client.mb_write(M_BASE_SENT_DATA, 1, buf2)

            # --- Pulse OK ---

            # 3. Show combined success message
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    "Wrote to DB and Pulsed %M150.0 successfully."
                ),
            )

        except Exception as e:
            # Handle errors from Write or Pulse
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", f"An error occurred:\n{e}")
            )
        
        finally:
            # 4. Re-enable the buttons
            if self.is_connected:
                self.root.after(0, lambda: self.btn_write_and_pulse.config(state="normal"))
                self.root.after(0, lambda: self.btn_reload.config(state="normal"))

    # ✅ Added: ฟังก์ชันสำหรับ Thread ของ Checkbutton
    def _write_line_use_bit_thread(self, bit: int, value: bool):
        threading.Thread(target=self._write_line_use_bit, args=(bit, value), daemon=True).start()

    # ✅ Added: ฟังก์ชันเขียนค่า Checkbutton (R-M-W)
    def _write_line_use_bit(self, bit: int, value: bool):
        if not self.is_connected:
            return
        
        try:
            # Disable Checkbuttons ชั่วคราว
            self.root.after(0, lambda: [chk.config(state="disabled") for chk in self.line_use_checks])

            # Read-Modify-Write
            with self._lock:
                buf = self.client.mb_read(M_BASE_LINE_USE, 1)
                util.set_bool(buf, 0, bit, value)
                self.client.mb_write(M_BASE_LINE_USE, 1, buf)
                
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Marker Write Error", f"An error occurred:\n{e}")
            )
        
        finally:
            # Re-enable Checkbuttons
            if self.is_connected:
                self.root.after(0, lambda: [chk.config(state="normal") for chk in self.line_use_checks])


    def on_close(self):
        self.is_running = False
        time.sleep(0.1)
        self.disconnect_plc()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlcApp(root)
    root.mainloop()