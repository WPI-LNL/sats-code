import tkinter as tk
import customtkinter as ctk
from time import strftime

# CONSTANTS
BIG_FONT = ("Arial", 64)
HEADER_FONT = ("Arial", 24)
STATUS_FONT = ("Arial", 18)
BODY_FONT = ("Arial", 16)

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        super().resizable(False, False)

        # Full Screen (Kiosk Mode)
        # super().bind("<Escape>", self.on_escape)
        # super().attributes("-fullscreen", True)
        # super().wm_attributes("-topmost", True)
        # super().focus_set()

        # Window configuration
        self.title("Small Asset Tracking System Kiosk")
        self.geometry(f"{800}x{480}")

        # Grid Layout
        self.grid_columnconfigure(1, weight=1) # Top status bar
        self.grid_rowconfigure((2,1), weight=1)

        # Top status bar
        self.status_bar = ctk.CTkFrame(self, fg_color=("white", "gray75"), corner_radius=0)
        self.status_bar.grid(row=0, column=0, columnspan=4, padx=0, pady=(0, 0), sticky="nsew")
        self.status_bar.grid_columnconfigure((1, 1, 1, 1, 1), weight=1)

        self.status_bar.online_status = ctk.CTkLabel(self.status_bar, text="Online", fg_color="light green", text_color="black", corner_radius=5, pady=10, padx=5, font=STATUS_FONT)
        self.status_bar.online_status.grid(row=0, column=3, padx=(20,10), pady=10, sticky="nsew")

        self.status_bar.time_display = ctk.CTkLabel(self.status_bar, fg_color=("gray95", "gray10"), text_color="black", corner_radius=5, pady=10, padx=5, font=STATUS_FONT)
        self.status_bar.time_display.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.update_time()

        self.help = ctk.CTkButton(self.status_bar, text="?", fg_color=("#3a7ebf", "#1f538d"), text_color=("white", "black"), border_width = 3,corner_radius=100, width=0, font=STATUS_FONT, command=self.display_help)
        self.help.grid(row=0, column=4, padx=(10,20), pady=10, sticky="nsew")

    def update_time(self):
        self.status_bar.time_display.configure(text=strftime('%H:%M %p'))
        self.after(60 * 1000, self.update_time)

    def on_escape(self, event=None):
        print("escaped")
        self.destroy()
        self.quit()
    
    def update_online(self, online = True):
        self.status_bar.online_status.configure(
            text="Online" if online else "Offline", 
            fg_color="light green" if online else "light red")
        
    def display_help(self):
        pass
        
    def init_bottom_prompt(self, text = None):    
        prompt = ctk.CTkLabel(self, text=text, fg_color=("gray85", "gray15"), text_color="black", corner_radius=5, pady=20, padx=20, font=HEADER_FONT)
        prompt.grid(row=3, column=1, padx=20, pady=10, sticky="s")
        return prompt

    def init_top_header(self, text = None):
        header = ctk.CTkLabel(self, text=text, fg_color=("gray85", "gray15"), text_color="black", corner_radius=5, pady=10, padx=25, font=STATUS_FONT)
        header.grid(row=0, column=1, padx=20, pady=10, sticky="n")
        return header

class IdleWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.top_header = super().init_top_header("Small Asset Tracking System")
        self.bottom_prompt = super().init_bottom_prompt("Scan WPI ID to begin")

class LoadingWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.top_header = super().init_top_header("Small Asset Tracking System")
        self.prompt = super().init_bottom_prompt("Standby...")
        self.progress = ctk.CTkProgressBar(self, fg_color=("gray85", "gray15"), corner_radius=15, mode="indeterminate", height=30, width=600)
        self.progress.grid(row=1, column=1, padx=20, pady=10, sticky="s")
        self.progress.start()
        

if __name__ == "__main__":
    app = LoadingWindow()
    # app.bind("<Button-1>", LoadingWindow())
    app.mainloop()


