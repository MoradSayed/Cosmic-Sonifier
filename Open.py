import os
import queue
import threading
from tkinter import filedialog
import numpy as np
import customtkinter as ctk
from Code import F2_Sonify
from loading_effect import load_ing
from Page_base_model import Page_BM
from Theme import *
from utils import hvr_clr_g
import json


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Open(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent, scrollable=False)
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.loader = load_ing(self.frame)
        self.thread_results = queue.Queue()

    def on_start(self):
        self.tool_menu()

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")
        
        self.folder_path = filedialog.askdirectory( initialdir = os.path.join(os.path.expanduser('~'), 'Desktop'),
                                                title = "Select a Folder",)
        if self.folder_path == "":
            self.folder_path = None
            self.menu_page_frame.page_switcher(self.menu_page_frame.last_page)

        if self.loader.state == "off" and self.folder_path != None:
            self.loader.start()

            # call the sonification function as a thread
            self.load_class = threading.Thread(target = self.load_data, args=(self.folder_path, self.thread_results))
            self.load_class.daemon = True # to stop the thread when the main thread stops
            self.load_class.start()
            self.check_thread_completion()

    def on_update(self):
        pass

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")

    def check_thread_completion(self):
        if self.load_class.is_alive():
            self.after(100, self.check_thread_completion)
        else:
            workspace_c = self.menu_page_frame.pages_dict["Workspace"]
            workspace_c.openable = True
            workspace_c.analization_output = self.thread_results.queue[-1]
            workspace_c.Snfy_img_path = self.folder_path + "/Snfy_img.jpg"

            self.loader.stop()
            self.menu_page_frame.page_switcher("Workspace")
            workspace_c.insert_data() 

    def load_data(self, folder_path, return_queue=None):
            data_opened = np.load(folder_path + '/Snfy_array.npz')
            opened_note = data_opened['arr_0']
            opened_vol  = data_opened['arr_1']
            # print(opened_note, opened_vol)

            with open (folder_path + "/Snfy_pref.json", "r") as f:
                json_vars = json.load(f)
            size = json_vars["size"]
            audio_full_time = json_vars["audio_full_time"]
            pixel_time = json_vars["pixel_time"]


            return_queue.put( ["Opened", size, opened_note, opened_vol, audio_full_time, pixel_time] )

