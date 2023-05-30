import tkinter as tk
import customtkinter as ctk
from time import strftime
import qrcode
from qrcode.image.pil import PilImage
from PIL import Image, ImageTk
from slot import Slot, SlotManager

# CONSTANTS
class FONT():
    BIG = ("Arial", 64)
    HEADER = ("Arial", 24)
    STATUS = ("Arial", 18)
    BODY = ("Arial", 16)

class COLOR():
    MAIN_BG = ("gray95", "gray10")
    STATUS_BAR_BG = ("white", "gray75")
    ONLINE_STATUS_BG = ("light green", "dark green")
    OFFLINE_STATUS_BG = ("coral2", "dark red")
    SYNC_STATUS_BG = ("light blue", "dark blue")
    HELP_BG = ("#3a7ebf", "#1f538d")

    ASSET_IN_BG = ("light green", "dark green")
    ASSET_SYNC_BG = ("light blue", "dark blue")
    ASSET_OUT_BG = ("white", "gray75")
    ASSET_UNKNOWN_BG = ("light yellow", "dark yellow")

    WARNING = ("pale goldenrod", "dark goldenrod")
    ERROR = ("coral2", "dark red")
    INFO = ("light blue", "dark blue")

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

root = ctk.CTk()
root.withdraw()
class MainWindow(ctk.CTkToplevel):
    def __init__(self, root=root):
        super().__init__()
        super().resizable(False, False)
        super().withdraw()

        # Close options
        super().bind("<Escape>", self.close)
        super().protocol("WM_DELETE_WINDOW", self.close)

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

        self.status_bar.online_status = ctk.CTkLabel(self.status_bar, text="Online", fg_color="light green", text_color="black", corner_radius=5, pady=10, padx=5, font=FONT.STATUS)
        self.status_bar.online_status.grid(row=0, column=3, padx=(20,10), pady=10, sticky="nsew")

        self.status_bar.time_display = ctk.CTkLabel(self.status_bar, fg_color=("gray95", "gray10"), text_color="black", corner_radius=5, pady=10, padx=5, font=FONT.STATUS)
        self.status_bar.time_display.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.update_time()

        self.help = ctk.CTkButton(self.status_bar, text="?", fg_color=("#3a7ebf", "#1f538d"), text_color=("white", "black"), border_width = 3,corner_radius=100, width=0, font=FONT.STATUS, command=self.display_help)
        self.help.grid(row=0, column=4, padx=(10,20), pady=10, sticky="nsew")

    def show(self):
        #super().attributes("-fullscreen", True)
        #super().wm_attributes("-topmost", True)
        #super().focus_set()
        self.deiconify()
    
    def hide(self):
        self.withdraw()

    def update_time(self):
        self.status_bar.time_display.configure(text=strftime('%-I:%M %p'))
        self.after(60 * 1000, self.update_time)

    def close(self, event=None):
        print("Closed.")
        self.destroy()
        self.quit()
    
    def update_online(self, online = True):
        self.status_bar.online_status.configure(
            text="Online" if online else "Offline", 
            fg_color="light green" if online else "coral2")
        
    def display_help(self):
        pass
        
    def init_bottom_prompt(self, text = None):    
        prompt = ctk.CTkLabel(self, text=text, fg_color=("gray85", "gray15"), text_color="black", corner_radius=5, pady=20, padx=20, font=FONT.HEADER)
        prompt.grid(row=3, column=1, padx=20, pady=10, sticky="s")
        return prompt
    
    def init_center_text(self, text = None, size = FONT.BIG[0], text_color = ("pale goldenrod", "dark goldenrod")):    
        center_text = ctk.CTkLabel(self, text=text, fg_color="pale goldenrod", text_color="black", corner_radius=5, pady=20, padx=20, font=FONT.BIG)
        center_text.grid(row=1, column=1, padx=20, pady=10, sticky="s")
        return center_text

    def init_top_header(self, text = None):
        header = ctk.CTkLabel(self, text=text, fg_color=("gray85", "gray15"), text_color="black", corner_radius=5, pady=10, padx=25, font=FONT.STATUS)
        header.grid(row=0, column=1, padx=20, pady=10, sticky="n")
        return header

class MessageWindow(MainWindow):
    def __init__(self, top_text = "Small Asset Tracking System", center_text = None, bottom_text = None):
        super().__init__()
        if top_text: self.top_header = super().init_top_header("Small Asset Tracking System")
        if center_text: self.center_text = super().init_center_text(center_text)
        if bottom_text: self.bottom_prompt = super().init_bottom_prompt(bottom_text)
        self.default_center_text = center_text
        self.default_bottom_text = bottom_text
    
    def showCenterAlert(self, text, timeout = None, fg_color = "gold"):
        self.center_text.configure(text=text, fg_color=fg_color)
        if timeout: self.after(timeout, self.clearCenterAlert)

    def clearCenterAlert(self):
        self.center_text.configure(text=self.default_center_text, fg_color=("pale goldenrod", "dark goldenrod"))

    def showBottomAlert(self, text, timeout = None, fg_color = "gold"):
        self.bottom_prompt.configure(text=text, fg_color=fg_color)
        if timeout: self.after(timeout, self.clearBottomAlert)

    def clearBottomAlert(self):
        self.bottom_prompt.configure(text=self.default_bottom_text, fg_color=("gray85", "gray15"))

class LoadingWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.top_header = super().init_top_header("Small Asset Tracking System")
        self.prompt = super().init_bottom_prompt("Standby...")
        self.progress = ctk.CTkProgressBar(self, fg_color=("gray85", "gray15"), corner_radius=15, mode="indeterminate", height=30, width=600)
        self.progress.grid(row=1, column=1, padx=20, pady=10, sticky="s")
        self.progress.start()

class QRWindow(MainWindow):
    def __init__(self, bottom_text = "Scan QR Code to register"):
        super().__init__()
        if bottom_text: self.prompt = super().init_bottom_prompt(bottom_text)
    
    def update_qrcode(self, url):
        self.dark_image = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=200, border=2, image_factory=PilImage)
        self.dark_image.add_data(url)
        #self.dark_image.make(fit=True)
        self.dark_image_pil = self.dark_image.make_image(fill_color=(237,232,177), back_color="black")._img
        self.light_image = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=200, border=2, image_factory=PilImage)
        self.light_image.add_data(url)
        #self.light_image.make(fit=True)
        self.light_image_pil = self.light_image.make_image(fill_color="black", back_color=(237,232,177))._img
        self.top_header = super().init_top_header("Small Asset Tracking System")
        
        self.qrcode = ctk.CTkImage(size=(300,300), light_image = self.light_image_pil, dark_image = self.dark_image_pil)
        self.center_image = ctk.CTkLabel(self, text=None, image=self.qrcode, fg_color="pale goldenrod", corner_radius=5, pady=20, padx=20, font=FONT.BIG)
        self.center_image.grid(row=1, column=1, padx=20, pady=10, sticky="s")

class SlotWidget(ctk.CTkButton):
    def __init__(self, m, slot:int, *args, **kwargs):
        super().__init__(m, *args, **kwargs)
        self.slot = slot
        self.configure(
            text_color="black",
            corner_radius=5,
            font=FONT.BODY,
            command=self.on_click)
        self.asset_removed()
    
    def searching(self):
        self.configure(fg_color = COLOR.ASSET_SYNC_BG, hover_color = "blue", text = "Searching...")
    
    def asset_added(self, asset):
        self.configure(fg_color = COLOR.ASSET_IN_BG, hover_color = "green", text = str(asset))

    def asset_removed(self):
        self.configure(fg_color = COLOR.ASSET_OUT_BG, hover_color = "grey", text = "")
    
    def on_click(self):
        pass # TODO: Implement slot/asset info page

class SlotWindow(MainWindow):
    def __init__(self, slot_manager):
        super().__init__()
        self.slot_manager = slot_manager
        self.top_header = super().init_top_header("Small Asset Tracking System")
        self.bottom_prompt = super().init_bottom_prompt("Add or remove assets")
        self.button_frame = ctk.CTkFrame(self, fg_color=("gray95", "gray10"), corner_radius=0)
        self.button_frame.grid(row=1, column=1, rowspan=2, padx=0, pady=(0, 0), sticky="nsew")
        self.button_frame.columnconfigure(tuple(range(5)), weight=1)
        self.button_frame.rowconfigure(tuple(range(4)), weight=1)
        self.port_list = []
        for y in range(4):
            for x in range(5):
                self.port_list.append(SlotWidget(self.button_frame, y*5 + x))
                if asset_list[y*5 + x]:
                    self.port_list[-1].asset_added(asset_list[y*5 + x])
                elif presence_list[y*5 + x]:
                    self.port_list[-1].searching()
                self.port_list[-1].grid(row=y, column=x, padx=10, pady=10, sticky="nsew")
    
    def update(self, asset_list, presence_list):
        for i in range(len(self.port_list)):
            if asset_list[i] != self.asset_list[i]:
                if asset_list[i]:
                    self.port_list[i].asset_added(asset_list[i])
                elif presence_list[i]:
                    self.port_list[i].searching()
                else:
                    self.port_list[i].asset_removed()
        

if __name__ == "__main__":
    from asset import Asset
    asset_list = [Asset(None, "Asset " + str(i), i, None) for i in range(20)]

    main = AssetWindow(asset_list, presence_list = [1 for i in range(20)])
    main.bind("<Return>", lambda event: main.update([0,0,0,0]+ [Asset(None, "Asset " + str(i), i, None) for i in range(4,16)] + [0,0,0,0], [1 for i in range(16)]+[0,0,0,0]))
    # main.bind("<Up>", lambda event: main.update())
    main.show()
    root.mainloop()