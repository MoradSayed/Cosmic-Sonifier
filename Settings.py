import json
from winreg import *

import customtkinter as ctk

from Page_base_model import Page_BM
from Theme import *
from utils import hvr_clr_g


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Settings(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent)
        self.window = window
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))

        self.settings_label = ctk.CTkLabel(self.frame, text="Settings", font=(FONT_B, 40))
        self.settings_label.pack(fill="x", padx=20, pady=20)

        # Section 1
        self.appearance_sec = self.section(section_parent= self.frame, Title="Appearance")
        # Section Units (options)
            # Combobox 
        self.theme_op   = self.section_unit(section=self.appearance_sec, title="Theme", widget="combobox", values=["System", "Light", "Dark"], command=self.theme_change, default=self.window.App_Theme.capitalize())
        #   # Button
        # self.Reset_op   = self.section_unit(section=self.appearance_sec, title="Reset to Default", widget="button", command= lambda: print("NO func implemented _Btn"), default= "Reset")
        #   # Checkbox
        # self.allow_op   = self.section_unit(section=self.appearance_sec, title="Allow Themes to Change", widget="checkbox", command= lambda: print("NO func implemented _Chk"))

        self.connection_sec = self.section(section_parent= self.frame, Title="Connection")
        # Section Units (options)
        with open('preferences.json', 'r') as f:
            data = json.load(f)
        self.AC_var = ctk.BooleanVar(value=data["auto_c"])
        self.auto_connect_op   = self.section_unit(section=self.connection_sec, title="Auto Connect to NASAs database", widget="checkbox", command= lambda : self.NASA_conn(self.auto_connect_op, "c"), default=self.AC_var)
        self.AL_var = ctk.BooleanVar(value=data["auto_l"]) 
        self.auto_load_op      = self.section_unit(section=self.connection_sec, title="Auto load from NASAs database", widget="checkbox", command= lambda : self.NASA_conn(self.auto_load_op    , "l"), default=self.AL_var)

    def section(self, section_parent, Title):
        section_frame = ctk.CTkFrame(section_parent, fg_color= "transparent")

        section_label = ctk.CTkLabel(section_frame, text=f"{Title}", font=(FONT_B, 25), anchor="w")
        section_label.pack(side="top", fill="x", padx=20)

        ops_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
        ops_frame.pack(fill="x", padx=20, pady=10)

        section_frame.pack(fill="x", pady=10)
        return section_frame

    def section_unit(self, section, title = "option", widget=None, command=None, values=None, default=None):
        unit_parent = section.winfo_children()[-1]
        unit_frame = ctk.CTkFrame(unit_parent, fg_color= "transparent")

        unit_label = ctk.CTkLabel(unit_frame, text=f"{title}", font=(FONT, 20))
        unit_label.pack(side="left", fill="x", padx=20, pady=10)

        if widget == "combobox" or widget == "ComboBox":
            unit_option = ctk.CTkComboBox(unit_frame, font=(FONT, 15), values = values, dropdown_font=(FONT, 15), state="readonly", command=command)
            unit_option.set(f"{default}")
            unit_option.pack(side="right", fill="x", padx=20, pady=10)


        if widget == "button" or widget == "Button":
            unit_option = ctk.CTkButton(unit_frame, text=f"{default}", font=(FONT, 15), command=command, fg_color=(LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent_btn"], "l", 20), hvr_clr_g(DARK_MODE["accent_btn"], "d", 20)))
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "checkbox" or widget == "CheckBox":
            unit_option = ctk.CTkCheckBox(unit_frame, text="", command=command, fg_color=(LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent_btn"], "l", 20), hvr_clr_g(DARK_MODE["accent_btn"], "d", 20)), onvalue=True, offvalue=False,)
            if default != None:
                unit_option.configure(variable=default) 
            unit_option.pack(side="right", fill="x", pady=10)

        unit_frame.pack(fill="x")

        return unit_frame

    def theme_change(self, event):
        new_theme = self.theme_op.winfo_children()[-1].get().lower()

        #changing the value of the theme in the preferences.json file
        with open('preferences.json', 'r') as f:
            theme_data = json.load(f)
        theme_data["theme"] = new_theme
        with open('preferences.json', 'w') as f:
            json.dump(theme_data, f, indent=4)

        #changing the color of the title bar
        if new_theme == "system":
            registry = ConnectRegistry(None, HKEY_CURRENT_USER)
            key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            mode = QueryValueEx(key, "AppsUseLightTheme")
            new_theme = 'light' if mode[0] else 'dark'
        self.window.title_bar_color(TITLE_BAR_HEX_COLORS[f"{new_theme}"])

        #changing the appearance mode of the app
        ctk.set_appearance_mode(f'{new_theme}')
        workshop_canvas = self.menu_page_frame.pages_dict["Workspace"].image_canvas
        workshop_canvas.configure(bg = hvr_clr_g(LIGHT_MODE["background"], "l") if new_theme == "light" else hvr_clr_g(DARK_MODE["background"], "d"))
        workshop_grapth = self.menu_page_frame.pages_dict["Workspace"].graph_canvas
        workshop_grapth.configure(bg = hvr_clr_g(LIGHT_MODE["background"], "l") if new_theme == "light" else hvr_clr_g(DARK_MODE["background"], "d"))        

    def NASA_conn(self, CB_widget, mode):
        selection = CB_widget.winfo_children()[-1].get()
        with open('preferences.json', 'r') as f:
            data = json.load(f)

        if selection == 1:
            if mode == "c":
                data["auto_c"] = True
            elif mode == "l":
                data["auto_l"] = True
        else:
            if mode == "c":
                data["auto_c"] = False
            elif mode == "l":
                data["auto_l"] = False
                
        with open('preferences.json', 'w') as f:
            json.dump(data, f, indent=4)


    def on_start(self):
        self.tool_menu()

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")

    def on_update(self):
        pass

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")