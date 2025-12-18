import sys
import os
import time
import datetime
import threading
import tkinter as tk
from tkinter import messagebox, font
import winreg 
import clr 
from PIL import Image, ImageTk 

# --- 作者與角色資訊 ---
APP_VERSION = "v1.3 Azrael Edition"
AUTHOR_NAME = "Aries Abriel Debrusc"
AUTHOR_EMAIL = "irosdp@gmail.com"
COPYRIGHT_YEAR = "2025"

# --- 設定區 ---
DLL_NAME = "LibreHardwareMonitorLib.dll"
IMAGE_NAME = "character.png"
ICON_NAME = "icon.ico"          # 新增：圖示檔名
DEFAULT_PSU_EFFICIENCY = 0.80  
BASE_LOAD_WATT = 50            

# --- 配色方案 ---
THEMES = {
    "dark": {
        "bg": "#2b2024",           
        "fg": "#FFD1DC",           
        "panel_bg": "#403036",     
        "highlight": "#FF69B4",    
        "entry_bg": "#605055",     
        "entry_fg": "white",       
        "btn_start": "#d63384",    
        "sub_text": "#aaaaaa"      
    },
    "light": {
        "bg": "#FFF0F5",           
        "fg": "#504044",           
        "panel_bg": "#FFE4E1",     
        "highlight": "#C71585",    
        "entry_bg": "white",
        "entry_fg": "black",
        "btn_start": "#FF69B4",
        "sub_text": "#666666"
    }
}

class PowerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"簡易電腦電費監測儀 {APP_VERSION}")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # --- 設定視窗圖示 (取代羽毛) ---
        self.set_window_icon() 
        # ---------------------------

        self.current_theme = THEMES["dark"] 
        
        self.is_running = False
        self.start_time = None
        self.total_kwh = 0.0
        self.monitor_thread = None
        
        suggested_rate, season_name = self.get_seasonal_rate()

        # --- 介面佈局 ---
        self.left_panel = tk.Frame(root, padx=20, pady=20)
        self.left_panel.pack(side="left", fill="both", expand=True)

        self.right_panel = tk.Frame(root, width=400)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        # --- 左側內容 ---
        self.header_font = font.Font(family="Microsoft JhengHei", size=18, weight="bold")
        self.lbl_title = tk.Label(self.left_panel, text=f"PC Power Monitor - {AUTHOR_NAME}", font=self.header_font)
        self.lbl_title.pack(anchor="w", pady=(0, 20))

        self.frame_setting = tk.Frame(self.left_panel, padx=15, pady=15)
        self.frame_setting.pack(fill="x", pady=10)
        
        self.lbl_season = tk.Label(self.frame_setting, text=f"當前季節: {season_name}", font=("Microsoft JhengHei", 10))
        self.lbl_season.pack(anchor="w")
        
        self.frame_rate = tk.Frame(self.frame_setting)
        self.frame_rate.pack(anchor="w", pady=5)
        
        self.lbl_rate_title = tk.Label(self.frame_rate, text="電費單價:", font=("Microsoft JhengHei", 12))
        self.lbl_rate_title.pack(side="left")
        
        self.entry_rate = tk.Entry(self.frame_rate, width=6, font=("Arial", 12), insertbackground="white")
        self.entry_rate.insert(0, str(suggested_rate))
        self.entry_rate.pack(side="left", padx=5)
        
        self.lbl_rate_unit = tk.Label(self.frame_rate, text="元/度", font=("Microsoft JhengHei", 12))
        self.lbl_rate_unit.pack(side="left")

        self.frame_time = tk.Frame(self.left_panel)
        self.frame_time.pack(anchor="w", pady=20)
        
        self.info_font = font.Font(family="Microsoft JhengHei", size=11)
        self.lbl_start_time = tk.Label(self.frame_time, text="開始: 未開始", font=self.info_font)
        self.lbl_start_time.pack(anchor="w")
        self.lbl_current_time = tk.Label(self.frame_time, text=f"現在: {datetime.datetime.now().strftime('%H:%M:%S')}", font=self.info_font)
        self.lbl_current_time.pack(anchor="w")
        self.lbl_duration = tk.Label(self.frame_time, text="時長: 00:00:00", font=self.info_font)
        self.lbl_duration.pack(anchor="w")

        self.frame_data = tk.Frame(self.left_panel)
        self.frame_data.pack(fill="x", pady=10)
        
        self.lbl_watts = tk.Label(self.frame_data, text="0 W", font=("Arial", 28, "bold"))
        self.lbl_watts.pack(anchor="w")
        self.lbl_watts_title = tk.Label(self.frame_data, text="即時耗電量", font=("Microsoft JhengHei", 10))
        self.lbl_watts_title.pack(anchor="w")

        self.lbl_daily_cost = tk.Label(self.frame_data, text="預估單日: $0", font=("Microsoft JhengHei", 12))
        self.lbl_daily_cost.pack(anchor="w", pady=(5, 20))

        self.lbl_cost = tk.Label(self.frame_data, text="$0.0", font=("Arial", 40, "bold"))
        self.lbl_cost.pack(anchor="w")
        self.lbl_cost_title = tk.Label(self.frame_data, text="累積電費 (TWD)", font=("Microsoft JhengHei", 12))
        self.lbl_cost_title.pack(anchor="w")

        self.frame_btn = tk.Frame(self.left_panel)
        self.frame_btn.pack(side="bottom", fill="x", pady=20)
        
        self.btn_start = tk.Button(self.frame_btn, text="開始監測", font=("Microsoft JhengHei", 12, "bold"), fg="white", activeforeground="white", relief="flat", command=self.start_monitoring)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
        
        self.btn_stop = tk.Button(self.frame_btn, text="停止", font=("Microsoft JhengHei", 12, "bold"), bg="#dc3545", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", command=self.stop_monitoring, state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=5)

        self.lbl_disclaimer = tk.Label(self.left_panel, text="*數值僅供參考，實際以台電為準", font=("Microsoft JhengHei", 8))
        self.lbl_disclaimer.pack(side="bottom", pady=5)

        self.create_menu()
        self.load_character_image()
        self.hardware_monitor = None
        self.load_dll()
        self.apply_system_theme()

    def set_window_icon(self):
        """設定視窗左上角的圖示"""
        # 取得正確的路徑 (相容 exe 與 python 模式)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()
            
        icon_path = os.path.join(base_path, ICON_NAME)
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Icon Load Error: {e}")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="關於 (About)", command=self.show_about_window)
        menubar.add_cascade(label="說明 (Help)", menu=help_menu)
        
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="Azrael Dark (深色)", command=lambda: self.switch_theme("dark"))
        theme_menu.add_command(label="Azrael Light (淺色)", command=lambda: self.switch_theme("light"))
        theme_menu.add_separator()
        theme_menu.add_command(label="跟隨系統 (System)", command=self.apply_system_theme)
        menubar.add_cascade(label="外觀 (Theme)", menu=theme_menu)
        
        self.root.config(menu=menubar)

    def switch_theme(self, mode):
        t = THEMES[mode]
        self.current_theme = t
        self.root.config(bg=t["bg"])
        self.left_panel.config(bg=t["bg"])
        self.right_panel.config(bg=t["bg"])
        self.frame_time.config(bg=t["bg"])
        self.frame_data.config(bg=t["bg"])
        self.frame_btn.config(bg=t["bg"])
        
        self.frame_setting.config(bg=t["panel_bg"])
        self.frame_rate.config(bg=t["panel_bg"])
        self.lbl_season.config(bg=t["panel_bg"], fg=t["fg"])
        self.lbl_rate_title.config(bg=t["panel_bg"], fg=t["fg"])
        self.lbl_rate_unit.config(bg=t["panel_bg"], fg=t["fg"])
        self.entry_rate.config(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"])
        
        self.lbl_title.config(bg=t["bg"], fg=t["highlight"])
        self.lbl_start_time.config(bg=t["bg"], fg=t["sub_text"])
        self.lbl_current_time.config(bg=t["bg"], fg=t["fg"])
        self.lbl_duration.config(bg=t["bg"], fg=t["highlight"])
        
        self.lbl_watts.config(bg=t["bg"], fg=t["fg"])
        self.lbl_watts_title.config(bg=t["bg"], fg=t["sub_text"])
        self.lbl_daily_cost.config(bg=t["bg"], fg="#e67e22") 
        
        self.lbl_cost.config(bg=t["bg"], fg=t["highlight"])
        self.lbl_cost_title.config(bg=t["bg"], fg=t["sub_text"])
        self.lbl_disclaimer.config(bg=t["bg"], fg=t["sub_text"])
        
        self.btn_start.config(bg=t["btn_start"])
        
        for widget in self.right_panel.winfo_children():
            widget.config(bg=t["bg"])

    def apply_system_theme(self):
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            mode = "light" if value == 1 else "dark"
            self.switch_theme(mode)
        except:
            self.switch_theme("dark")

    def show_about_window(self):
        about_text = (
            f"簡易電腦電費監測儀\n"
            f"{APP_VERSION}\n\n"
            f"作者: {AUTHOR_NAME}\n"
            f"聯絡: {AUTHOR_EMAIL}\n\n"
            f"Copyright © {COPYRIGHT_YEAR} All Rights Reserved.\n"
            "Powered by LibreHardwareMonitor"
        )
        messagebox.showinfo("關於", about_text)

    def load_character_image(self):
        if getattr(sys, 'frozen', False): base_path = sys._MEIPASS
        else: base_path = os.getcwd()
        img_path = os.path.join(base_path, IMAGE_NAME)
        if os.path.exists(img_path):
            try:
                pil_image = Image.open(img_path)
                window_height = 650
                ratio = window_height / pil_image.height
                new_width = int(pil_image.width * ratio)
                new_height = window_height
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(pil_image)
                for widget in self.right_panel.winfo_children(): widget.destroy()
                lbl_img = tk.Label(self.right_panel, image=self.photo_image, bg=self.current_theme["bg"])
                lbl_img.pack(side="bottom", anchor="se")
                self.right_panel.config(width=new_width)
            except: pass

    def get_seasonal_rate(self):
        month = datetime.datetime.now().month
        if 6 <= month <= 9: return 5.5, "夏月 (6-9月)"
        else: return 4.0, "非夏月"

    def load_dll(self):
        if getattr(sys, 'frozen', False): base_path = sys._MEIPASS
        else: base_path = os.getcwd()
        dll_path = os.path.join(base_path, DLL_NAME)
        if not os.path.exists(dll_path): return False
        try:
            clr.AddReference(dll_path)
            from LibreHardwareMonitor.Hardware import Computer
            self.computer = Computer()
            self.computer.IsCpuEnabled = True
            self.computer.IsGpuEnabled = True
            self.computer.Open()
            return True
        except: return False

    def get_power_draw(self):
        if not self.computer: return 0.0
        cpu_w, gpu_w = 0.0, 0.0
        try:
            for hardware in self.computer.Hardware:
                hardware.Update()
                for sensor in hardware.Sensors:
                    if str(sensor.SensorType) == "Power":
                        if "CPU Package" in sensor.Name: cpu_w = max(cpu_w, sensor.Value or 0)
                        if str(hardware.HardwareType).startswith("Gpu"):
                            if sensor.Value and sensor.Value > gpu_w: gpu_w = sensor.Value
        except: pass
        return cpu_w, gpu_w

    def start_monitoring(self):
        if self.is_running: return
        try: self.rate_price = float(self.entry_rate.get())
        except: return
        self.is_running = True
        self.start_time = datetime.datetime.now()
        self.total_kwh = 0.0
        self.lbl_start_time.config(text=f"開始: {self.start_time.strftime('%H:%M:%S')}")
        self.btn_start.config(state="disabled", bg="#555555")
        self.btn_stop.config(state="normal", bg="#dc3545")
        self.entry_rate.config(state="disabled")
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.is_running = False
        self.btn_start.config(state="normal", bg=self.current_theme["btn_start"])
        self.btn_stop.config(state="disabled", bg="#555555")
        self.entry_rate.config(state="normal")

    def monitor_loop(self):
        last_time = time.time()
        while self.is_running:
            now = time.time()
            dt = now - last_time
            last_time = now
            cpu_w, gpu_w = self.get_power_draw()
            wall_w = (cpu_w + gpu_w + BASE_LOAD_WATT) / DEFAULT_PSU_EFFICIENCY
            self.total_kwh += (wall_w / 1000) * (dt / 3600)
            self.root.after(0, self.update_gui, wall_w)
            time.sleep(1)

    def update_gui(self, current_watts):
        now = datetime.datetime.now()
        self.lbl_current_time.config(text=f"現在: {now.strftime('%H:%M:%S')}")
        if self.start_time:
            delta = now - self.start_time
            self.lbl_duration.config(text=f"時長: {str(delta).split('.')[0]}")
        total_cost = self.total_kwh * self.rate_price
        daily_est = (current_watts * 24 / 1000) * self.rate_price
        
        self.lbl_watts.config(text=f"{int(current_watts)} W")
        self.lbl_daily_cost.config(text=f"預估單日: ${int(daily_est)}")
        self.lbl_cost.config(text=f"${total_cost:.2f}")

if __name__ == "__main__":
    try: is_admin = os.getuid() == 0
    except:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    root = tk.Tk()
    app = PowerMonitorApp(root)
    root.mainloop()