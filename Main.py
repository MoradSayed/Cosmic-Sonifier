import json

import customtkinter as ctk

try:
    from ctypes import byref, c_int, sizeof, windll 
except:
    pass
from Tab_Page_Frame import Frame
from Theme import *


class Desert(ctk.CTk):

    def __init__ (self):
        super().__init__(fg_color= (LIGHT_MODE["background"], DARK_MODE["background"]))
        self.title("")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f'1200x800+{int((screen_width*1.5/2)-(1200*1.5/2))}+{int((screen_height*1.5/2)-(800*1.5/2))}') #1.5 for the window scale (150%)
#        self.resizable(False, False) #Temp approach till a solution is found to resizing with a constant aspect ratio
        self.minsize(screen_width/2, screen_height/2)
#        self.maxsize(2160/1.5, 1440/1.5) #1.5 for the Windows OS Display Scale (150%)
        try:
            self.iconbitmap("images/empty.ico")
        except:
            pass

        with open('preferences.json', 'r') as f:
            theme_data = json.load(f)
        self.App_Theme = theme_data["theme"]
        ctk.set_appearance_mode(f'{self.App_Theme}')
        self.theme_mode = ctk.get_appearance_mode()
        self.title_bar_color(TITLE_BAR_HEX_COLORS[f"{self.theme_mode.lower()}"]) #change the title bar color


        self.call_page()

        self.mainloop()

    def call_page(self):
        self.Home = Frame(self, "Home")

    def title_bar_color(self, color):
        try:
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetParent(self.winfo_id()), 
                35, 
                byref(c_int(color)), 
                sizeof(c_int)
                )
        except:
            pass


if __name__ == "__main__":
    main_window = Desert()