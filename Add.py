import os
import queue
import threading
from tkinter import filedialog

import customtkinter as ctk

from Code import F1_analize_and_map
from loading_effect import load_ing
from Page_base_model import Page_BM
from Theme import *
from utils import hvr_clr_g


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Add(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent, scrollable=False)
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.loader = load_ing(self.frame)
        self.thread_results = queue.Queue()
        self.home_image = None

    def on_start(self):
        self.tool_menu()

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.home_image == None:
            self.file_path = filedialog.askopenfilename( initialdir = os.path.join(os.path.expanduser('~'), 'Desktop'),
                                                    title = "Select a File",
                                                    filetypes = (("Images", "*.jpg*"), ))
            if self.file_path == "":
                self.file_path = None
                self.menu_page_frame.page_switcher(self.menu_page_frame.last_page)
        else:
            self.file_path = None

        if self.loader.state == "off" and (self.file_path != None or self.home_image != None):
            self.loader.start()

            # call the sonification function as a thread
            self.sonification_class = threading.Thread(target = F1_analize_and_map.Sonify, args=(self.home_image, self.file_path, self.thread_results))
            self.sonification_class.daemon = True # to stop the thread when the main thread stops
            self.sonification_class.start()
            self.check_thread_completion()

    def on_update(self):
        pass

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")

    def check_thread_completion(self):
        if self.sonification_class.is_alive():
            self.after(100, self.check_thread_completion)
        else:
            workspace_c = self.menu_page_frame.pages_dict["Workspace"]
            workspace_c.openable = True
            workspace_c.analization_output = self.thread_results.queue[-1]
            workspace_c.Snfy_img_path = self.file_path

            self.loader.stop()
            self.menu_page_frame.page_switcher("Workspace")
            workspace_c.insert_data(self.home_image) 

        
