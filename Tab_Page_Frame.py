import customtkinter as ctk
from PIL import Image

from Theme import *
from utils import hvr_clr_g

from Workspace import Workspace
from Home import Home
from Add import Add
from Open import Open
from Settings import Settings


class Frame(ctk.CTkFrame):
    
    def __init__ (self, parent, page_choise):
        super().__init__(parent, fg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
        self.window = parent

        self.menu_relwidth = 0.05
        self.menu_relx = 0
        self.padding = 0.02
        self.menu_opened = False

        self.page_choise = page_choise
        self.last_page = None
        self.tabs = [("Workspace", 0), ("Home", 1), ("Add", 1), ("Open", 1), ("Settings", 0)] #used to add tabs after importing its class, the 1 or 0 is used to determine if the tab is created at the beginning automatically or do i want to create it manually later 
        self.buttons = {}               #used to save all the tab buttons for later configuration
        self.pages_dict = {}            #used to save the frame classes of all the tabs, (ex: home frame, friends frame, etc...)

        self.window.update()
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.window.bind("<Configure>", self.update_sizes)

        self.menu()
        self.page()

        self.pack(expand = True, fill = "both")

        self.pages_dict[self.page_choise].called_when_opened()   # used to apply some changes to the default page, that can't be applied before the frame is displayed  
        
    def menu(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))

        # 1
        self.logo_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        # button = ctk.CTkButton(self.logo_frame, text="", fg_color="transparent", hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), image=ctk.CTkImage(Image.open("images/Icons/Logo_c.png"), Image.open("images/Icons/Logo_c.png"), (45,45)))
        # button.pack(pady=5)
        button = self.tab("Workspace", self.logo_frame, (45,45))
        self.buttons["Workspace"] = button
        self.logo_frame.pack(fill="x", ipady=5, padx=5)

        # 2
        self.tabs_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        for tab in self.tabs:
            if tab[1] == 1:
                button = self.tab(tab[0], self.tabs_frame)      #create all the tabs
                self.buttons[tab[0]] = button #saving them for later configuration in the color
            else:
                continue
        self.tabs_frame.pack(fill="x", padx=5, pady = 5)    

        self.white_line_spacer(self.menu_frame)                                         # white line
        #3
        self.apps_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")

        self.apps_frame.pack(fill="both", expand=True, padx=5, pady = 5)

        self.white_line_spacer(self.menu_frame)                                         # white line
        #4
        self.user_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        button = self.tab("Settings", self.user_frame)
        self.buttons["Settings"] = button
        self.user_frame.pack(fill="x", padx=5)

        self.menu_frame.place(relx=self.menu_relx, rely=0, anchor="nw", relheight = 1-(25/self.window_height), relwidth = self.menu_relwidth)

    def page(self):
        self.page_frame = ctk.CTkFrame(self, fg_color="transparent")

        for name in self.tabs:
            self.pages_dict[name[0]] = eval(name[0] + "(self.window, self, self.page_frame)")    #calls all the contents of the tabs (but not displaying them) and passing the arguments, while saving them in a dict for later use
            if self.pages_dict[name[0]].scrollable:
                Last_widget = ctk.CTkFrame(self.pages_dict[name[0]].Scrollable_frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d"))) #created to locate the y position for the edge of the frame
                Last_widget.pack(fill="x", pady=10)


        self.pages_dict[self.page_choise].pack(expand=True, fill="both")                        #display the default page
        self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(f"images/Icons/{self.page_choise}_b_s.png"), Image.open(f"images/Icons/{self.page_choise}_w_s.png"), (30,30)))


        self.page_frame.place(relx= (self.menu_relx + self.menu_relwidth + (self.padding/2)) , 
                              rely=0, 
                              anchor="nw", 
                              relheight = 1-(25/self.window_height), 
                              relwidth = 1 - (self.menu_relx + self.menu_relwidth + (self.padding/2)) - (self.padding/2)
                              )
           
    def menu_button_command(self): # currently not used
        if self.menu_opened:
            self.menu_relwidth -= 0.135
            self.menu_frame.place(relx=self.menu_relx, rely=0, anchor="nw", relheight = 1-(40/self.window.winfo_width()), relwidth = self.menu_relwidth)

            self.page_frame.place(relx= (self.menu_relx + self.menu_relwidth + (self.padding/2)) , 
                                rely=0, 
                                anchor="nw", 
                                relheight = 1-(40/self.window.winfo_width()), 
                                relwidth = 1 - (self.menu_relx + self.menu_relwidth + (self.padding/2)) - (self.padding/2)
                                )

            self.update()
            self.menu_opened = False

        else:
            self.menu_relwidth += 0.135
            self.menu_frame.place(relx=self.menu_relx, rely=0, anchor="nw", relheight = 1-(40/self.window.winfo_width()), relwidth = self.menu_relwidth)

            self.page_frame.place(relx= (self.menu_relx + self.menu_relwidth + (self.padding/2)) , 
                                    rely=0, 
                                    anchor="nw", 
                                    relheight = 1-(40/self.window.winfo_width()), 
                                    relwidth = 1 - (self.menu_relx + self.menu_relwidth + (self.padding/2)) - (self.padding/2)
                                    )
            self.update()
            self.menu_opened = True

    def tab(self, tab, parent, btn_size=(30,30)):
        button = ctk.CTkButton(parent, text="", fg_color="transparent", hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), image=ctk.CTkImage(Image.open(f"images/Icons/{tab.lower()}_b.png"), Image.open(f"images/Icons/{tab.lower()}_w.png"), btn_size), command = lambda: self.page_switcher(f'{tab}'))
        button.pack(ipadx = 10, pady=10)
        return button

    def page_switcher(self, buttonID):
        if buttonID != self.page_choise and not(buttonID == "Workspace" and self.pages_dict[buttonID].openable == False):
            self.pages_dict[self.page_choise].pack_forget()
            self.pages_dict[self.page_choise].tools_f.place_forget()    #placed inside the file 
            self.buttons[self.page_choise].configure(image=ctk.CTkImage(Image.open(f"images/Icons/{self.page_choise.lower()}_b.png"), Image.open(f"images/Icons/{self.page_choise.lower()}_w.png"), (45,45) if self.page_choise == "Workspace" else (30,30)))
            self.last_page = self.page_choise
            # print(self.page_choise, ">>", buttonID)
            self.page_choise = f'{buttonID}'
            self.buttons[buttonID].configure(image=ctk.CTkImage(Image.open(f"images/Icons/{buttonID.lower()}_b_s.png"), Image.open(f"images/Icons/{buttonID.lower()}_w_s.png"), (45,45) if buttonID == "Workspace" else (30,30)))
            self.pages_dict[buttonID].pack(expand=True, fill="both")
            self.pages_dict[buttonID].called_when_opened()   # used to apply some changes that can't be applied before the frame is displayed

    def update_sizes(self, event):
        if (event.width != self.window_width or event.height != self.window_height) and (event.widget == self.window):
            self.window_width = event.width
            self.window_height = event.height
            self.menu_relwidth = 75/self.window_width
            
            self.menu_frame.place(relx=self.menu_relx, rely=0, anchor="nw", relheight = 1-(25/self.window_height), relwidth = self.menu_relwidth)
            
            self.page_frame.place(relx= (self.menu_relx + self.menu_relwidth + (self.padding/2)) , 
                        rely=0, 
                        anchor="nw", 
                        relheight = 1-(25/self.window_height), 
                        relwidth = 1 - (self.menu_relx + self.menu_relwidth + (self.padding/2)) - (self.padding/2)
                        )
            
            self.pages_dict[self.page_choise].update_size_BM() #calls the update function for the displayed page
            
    def white_line_spacer(self, parent):
        self.line = ctk.CTkFrame(parent, fg_color=("#b3b3b3","#4c4c4c"), width=2, height=2)
        self.line.pack(fill="x", padx=10)

