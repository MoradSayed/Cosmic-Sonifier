import json
import queue
import textwrap
import threading

import customtkinter as ctk
import requests
from DBRequests import fetch_images
from Page_base_model import Page_BM
from PIL import Image
from Theme import *
from utils import hvr_clr_g
from VC import SR_Class


# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Home(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent)
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))

        self.mode = ctk.get_appearance_mode()
        self.c = 1 # multiplier for y padding 
        
        self.n_image_size = 250
        self.image_count = queue.Queue()
        self.image_count.put(-1)
        self.image_render_limit = 15
        self.pages = []
        with open('preferences.json', 'r') as f:
            data = json.load(f)
        self.automatic_loading = data["auto_l"]

        self.Recent  = self.frame_template("Recent", "label")
        self.NASAsDB = self.frame_template("NASA Image Library", None)
        self.load_more_btn = ctk.CTkButton(self.frame, text="Load", font=(FONT, 20), fg_color=(LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), 
                                           hover_color=(hvr_clr_g(LIGHT_MODE["accent_btn"], "l", 20), hvr_clr_g(DARK_MODE["accent_btn"], "d", 20)), 
                                           command = lambda: self.loadmore_func(), state="disabled")
        self.load_more_btn.pack(pady=10*self.c)

        self.NASAAPI_result = queue.Queue()
        self.NASAAPI_reqs = threading.Thread(target= fetch_images, args=(1, "space stars", self.NASAAPI_result))
        self.NASAAPI_reqs.daemon = True
        self.NASAAPI_reqs.start()

        self.check_thread_completion()

        self.nasa_images_queue = queue.Queue()

        # recognizer part
        self.recognizer_state = 0
        window.bind("<KeyPress>", self.call_recognizer)


    def on_start(self):
        self.tool_menu()
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")

    def on_update(self):
        pass

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")

    def check_thread_completion(self):
        if self.NASAAPI_reqs.is_alive():
            self.window.after(100, self.check_thread_completion)
            # print("yet")
        else:
            if self.automatic_loading == True:
                # print("Loading")
                self.create_imgs_thread = threading.Thread(target= self.put_images, args=(self.nasa_images_queue, ))
                self.create_imgs_thread.daemon = True
                self.create_imgs_thread.start()
            else:
                # print("not loading")
                self.load_more_btn.configure(state="normal")

    def put_images(self, images_queue=None):
            
            if self.NASAAPI_result is not None:
                for i in range(self.image_count.queue[0], self.image_count.queue[0]+self.image_render_limit):
                    Web_Img_title = self.NASAAPI_result.queue[-1][i]["data"][0]["title"]
                    Web_Img_Link  = self.NASAAPI_result.queue[-1][i]["links"][0]["href"] 
                    im = Image.open(requests.get(Web_Img_Link, stream=True).raw)
                    images_queue.put(im)
                    # print(images_queue.queue)
                    self.image_count.queue[0] += 1
                    # print("new >>", self.image_count.queue[0])
                    w, h = im.size[0],im.size[1]
                    r = w/h
                    s = (self.n_image_size, int(self.n_image_size/r))
                    im_ctk = ctk.CTkImage(im, size=s)
                    self.add_tab(self.NASAsDB, Web_Img_title, im_ctk, "s")
                self.load_more_btn.configure(state="normal")
    
    def frame_template(self, title, size):
        parent_f = ctk.CTkFrame(self.frame, fg_color="transparent")

        title = ctk.CTkLabel(parent_f, text=f"{title}", font=(FONT, 30), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="w")
        title.pack(fill="x", padx=20, pady=20*self.c)

        if size == "l":
            self.large(parent_f)
        elif size == "s":
            self.small(parent_f)
        elif size == "label":
            self.Label_func(parent_f)

        parent_f.pack(fill="x", pady=10*self.c)

        return parent_f

    def large(self, parent_f, text, image):
        tab_cont = ctk.CTkFrame(parent_f, fg_color="transparent", height=300, width=self.frame.winfo_width())

        tabs_f = ctk.CTkButton(tab_cont, fg_color=(LIGHT_MODE["activated_frame"], DARK_MODE["activated_frame"]), height=400, width=350, 
                               text=f"{text}", image=image, compound="top", )
        tabs_f.pack(padx=20, pady=10*self.c)
        
        tab_cont.pack(expand=True, fill="both")

    def small(self, parent_f, text, image):
        # color = (LIGHT_MODE["activated_frame"], DARK_MODE["activated_frame"])
        tab_cont = ctk.CTkFrame(parent_f, fg_color="transparent", height=300, width=self.frame.winfo_width())

        tab_img = ctk.CTkButton(tab_cont, fg_color="transparent", text="", image=image, hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        tab_img.pack(padx=20, pady=10*self.c, side="left")

        tab_cont.update()
        tit_f   = ctk.CTkFrame(tab_cont, fg_color="transparent",)
        newtext = textwrap.shorten(text, 50)
        tab_tit = ctk.CTkLabel(tit_f, fg_color="transparent", text=f"{newtext}", font=(FONT, 20), anchor="w")
        tab_tit.pack(fill = "both", expand = True)
        tit_f.pack(pady=10*self.c, fill = "x", expand = True, side="left")

        add_btn = ctk.CTkButton(tab_cont, width=30, height=30, text="+", font=(FONT_B, 30),  
                                fg_color=(LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), 
                                hover_color=(hvr_clr_g(LIGHT_MODE["accent_btn"], "l", 20), hvr_clr_g(DARK_MODE["accent_btn"], "d", 20)), 
                                command= lambda num = self.image_count.queue[0]: self.add_image_btn_command(num))
        add_btn.place(relx=0.975, rely=0.5, anchor="e")

        tab_cont.pack(expand=True, fill="both", pady=10)

        White_line = ctk.CTkFrame(parent_f, fg_color=(DARK_MODE["background"], LIGHT_MODE["background"]), height=2)
        White_line.pack(fill="x", expand=True, padx = 20)
    
    def add_tab(self, frame, text=None, image=None, size=None):
        if size == "l":
            self.large(frame, text, image)
        elif size == "s":
            self.small(frame, text, image)
        self.called_when_opened()

    def Label_func(self, parent_f):
        l_widget = ctk.CTkLabel(parent_f, text="No Recent projects", font=(FONT, 20), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="center")
        l_widget.pack(fill="x", padx=20, pady=10*self.c, expand=True)

    def add_image_btn_command(self, index):
        # this is the image "self.nasa_images_queue.queue[index]"
        self.menu_page_frame.pages_dict["Add"].home_image = self.nasa_images_queue.queue[index]
        self.menu_page_frame.page_switcher("Add")
    
    def loadmore_func(self):
        self.load_more_btn.configure(state="disabled")
        self.create_imgs_thread = threading.Thread(target= self.put_images, args=(self.nasa_images_queue, ))
        self.create_imgs_thread.daemon = True
        self.create_imgs_thread.start()

    # recognizer part
    def call_recognizer(self, event):
        if event.char == "f" and self.recognizer_state == 0:
            self.recognizer_state = 1
            print("f pressed")
            self.sr_thread = threading.Thread(target=SR_Class, args=(self.menu_page_frame, ))
            self.sr_thread_daemon = True
            self.sr_thread.start()

            self.check_SR_result()
        else:
            # print("wrong key pressed")
            pass

    def check_SR_result(self):
        if self.sr_thread.is_alive():
            self.after(100, self.check_SR_result)
        else:
            self.recognizer_state = 0