import json
import tkinter as tk
import os
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog
from Code import F2_Sonify
from Page_base_model import Page_BM
from Theme import *
from utils import hvr_clr_g
import threading, queue

# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Workspace(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent, scrollable=False)
        self.window = window
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame
        self.openable = False
        self.frame.configure()
        self.analization_output = None          # this will be the output of the sonification function (from the analization stage)
        self.Snfy_img_path = None
        self.v_slider_default = None
        self.t_slider_default = None
        self.playing = False
        self.stop_thread_queue = queue.Queue()
        self.stop_thread_queue.put(True)

        with open('preferences.json', 'r') as f:
            theme_data = json.load(f)
        self.mode = theme_data["theme"]
        self.canvas_bg = hvr_clr_g(LIGHT_MODE["background"], "l") if self.mode == "light" else hvr_clr_g(DARK_MODE["background"], "d")

        self.frame.columnconfigure(0, weight=50, uniform="c")
        self.frame.columnconfigure(1, weight=1,  uniform="c")
        self.frame.columnconfigure(2, weight=20, uniform="c")
        self.frame.rowconfigure   (0, weight=1)
        
        self.canvas_frame = ctk.CTkFrame(self.frame, fg_color=(LIGHT_MODE["background"], DARK_MODE["background"]), bg_color = (LIGHT_MODE["background"], DARK_MODE["background"]))
        self.canvas()
        self.playback_controls()
        self.graphCanvas()
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.menu_frame   = ctk.CTkFrame(self.frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), bg_color = (LIGHT_MODE["background"], DARK_MODE["background"]))
        self.menu()
        self.menu_frame.grid(row=0, column=2, sticky="nsew")
        
    def on_start(self):
        self.tool_menu()

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")
        
        self.scrollable_area.update()
        self.menu_canvas.create_window(
            (0,0),
            window=self.Scrollable_menu_frame,
            anchor="nw",
            width = self.scrollable_area.winfo_width(),
            height = 10000,
            tags= "frame")
        
        
        self.menu_frame.update()
        self.max_height = self.menu_last_block.winfo_y()

        self.menu_canvas.configure(scrollregion=(0, 0, self.scrollable_area.winfo_width(), self.max_height))

        if self.max_height > self.scrollable_area.winfo_height():
            self.menu_canvas.bind_all("<MouseWheel>", lambda event: self.menu_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        else:
            self.menu_canvas.unbind_all("<MouseWheel>")

    def on_update(self):
        self.img_cnvs_frm.update()
        self.cnvsw, self.cnvsh = (self.img_cnvs_frm.winfo_width(), self.img_cnvs_frm.winfo_height())
        cnvs_ratio = self.cnvsw/self.cnvsh

        self.img_open= self.img_open.resize(( int(self.cnvsw) , int(self.cnvsw/(self.img_w/self.img_h)) ) if cnvs_ratio <= self.img_ratio else ( int(self.cnvsh*(self.img_w/self.img_h)) , int(self.cnvsh) ))
        self.img_tk  = ImageTk.PhotoImage(self.img_open)
        self.image_canvas.delete("snfy_img")
        self.image_canvas.create_image(int(self.cnvsw/2), int(self.cnvsh/2), image=self.img_tk, anchor="center", tag="snfy_img")

        self.scrollable_area.update()
        self.menu_canvas.itemconfigure("frame", width=self.scrollable_area.winfo_width())
        print(self.max_height, self.scrollable_area.winfo_height())        
        if self.max_height > self.scrollable_area.winfo_height():
            self.menu_canvas.bind_all("<MouseWheel>", lambda event: self.menu_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        else:
            self.menu_canvas.unbind_all("<MouseWheel>")

    def canvas(self):
        self.img_cnvs_frm = ctk.CTkFrame(self.canvas_frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.image_canvas = tk.Canvas(self.img_cnvs_frm, bg=self.canvas_bg, highlightthickness=0, relief="ridge", bd=0)
        self.image_canvas.pack(fill="both", expand=True)
        self.img_cnvs_frm.place(relx=0, rely=0, relwidth=1, relheight=0.65)

    def playback_controls(self):
        self.playback_frame = ctk.CTkFrame(self.canvas_frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        
        self.controls_container = ctk.CTkFrame(self.playback_frame, fg_color="transparent")
        self.play_b = ctk.CTkButton(self.controls_container, text="", command= lambda: self.play_btn_func(), 
                                    fg_color="transparent", 
                                    hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), 
                                    width=30, height=30, image=ctk.CTkImage(Image.open(f"images/Icons/play_b.png"), Image.open(f"images/Icons/play_w.png"), (40, 40)))
        self.play_b.pack(side="left", pady=10)

        self.stop_b = ctk.CTkButton(self.controls_container, text="", command= lambda: self.stop_btn_func(), 
                                    fg_color="transparent", 
                                    hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), 
                                    width=30, height=30, image=ctk.CTkImage(Image.open(f"images/Icons/stop_b.png"), Image.open(f"images/Icons/stop_w.png"), (30, 30)))
        self.stop_b.pack(side="left", pady=10)

        # self.output_MIDI_b = ctk.CTkButton(self.playback_frame, text="output MIDI", command= lambda: self.SNFY_C_Class.create_MIDI())
        # self.output_MIDI_b.pack(side="left", padx=10, pady=10)

        # self.play_MIDI_b = ctk.CTkButton(self.playback_frame, text="MIDI Speaks", command= lambda: self.SNFY_C_Class.play_MIDI_to_pyo())
        # self.play_MIDI_b.pack(side="left", padx=10, pady=10)
        
        self.controls_container.pack(padx=20)
        self.playback_frame.place(relx=0, rely=0.67, relwidth=1, relheight=0.1)

    def play_btn_func(self):
        if self.playing == False:
            self.playing = True
            self.stop_thread_queue.put(True)
            self.play_thread = threading.Thread(target=self.SNFY_C_Class.create_normal_pyo, args=[self.stop_thread_queue, ])
            self.play_thread.daemon = True
            self.play_thread.start()
            self.check_play_completion()

    def check_play_completion(self):
        if self.play_thread.is_alive():
            self.window.after(100, self.check_play_completion)
        else:
            self.playing = False

    def stop_btn_func(self):
        self.stop_thread_queue.put(False)

    def graphCanvas(self):
        self.graph_canvas = tk.Canvas(self.canvas_frame, bg=self.canvas_bg, highlightthickness=0, relief="ridge", bd=0)
        self.graph_canvas.place(relx=0, rely=0.79, relwidth=1, relheight=0.21)

    def menu(self):
        self.name = ctk.CTkLabel(self.menu_frame, text=f"new project", font=(FONT, 20), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="w")
        self.name.pack(fill="x", padx=20, pady=10)

        self.white_line = ctk.CTkFrame(self.menu_frame, fg_color=(DARK_MODE["background"], LIGHT_MODE["background"]), height=2)
        self.white_line.pack(fill="x", padx = 20)

        self.scrollable_area = ctk.CTkFrame(self.menu_frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.scrollable_area.pack(fill="both", expand=True, padx = 20)

        self.menu_canvas = tk.Canvas(self.scrollable_area, background=self.canvas_bg, scrollregion = (0, 0, self.scrollable_area.winfo_width(), 10000), highlightthickness=0, relief="ridge", bd=0)
        self.menu_canvas.pack(fill="both", expand=True)

        self.Scrollable_menu_frame = ctk.CTkFrame(self.menu_canvas, fg_color="transparent", bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))

        self.menu_content()

        self.menu_last_block = ctk.CTkFrame(self.Scrollable_menu_frame, fg_color="transparent", bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.menu_last_block.pack()

    def menu_content(self):
        parent = self.Scrollable_menu_frame

        slider_1 = self.slide_bar_op(title="Volume", min=0, max=150, default=90)
        slider_2 = self.slide_bar_op(title="Time (s)", min=30, max=90, default=45)

    def slide_bar_op(self, title, min, max, default=None):

        slide_bar_F = ctk.CTkFrame(self.Scrollable_menu_frame, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), 
                                   bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))

        slide_bar = ctk.CTkSlider(slide_bar_F, from_=min, to=max, orientation="horizontal", number_of_steps= max-min,
                                  fg_color=(LIGHT_MODE["accent_S_btn"], DARK_MODE["accent_S_btn"]), 
                                  progress_color= (LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), 
                                  command= lambda event: self.slider_command(event, title, value_label), 
                                  button_color=(LIGHT_MODE["accent_btn"], DARK_MODE["accent_btn"]), 
                                  button_hover_color=(hvr_clr_g(LIGHT_MODE["accent_btn"], "l"), hvr_clr_g(DARK_MODE["accent_btn"], "d")))
        if default != None:
            slide_bar.set(default)
            if title == "Volume":
                self.v_slider_default = default/10
            elif title == "Time (s)":
                self.t_slider_default = default

        label_frame = ctk.CTkFrame(slide_bar_F, fg_color="transparent")
        title_label = ctk.CTkLabel(label_frame, text=title, font=(FONT, 15), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="w")
        title_label.pack(fill="x", side="left")

        value_label = ctk.CTkLabel(label_frame, text=f"{int(slide_bar.get())}", font=(FONT, 15), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="e")
        value_label.pack(fill="x", side="right")
        label_frame.pack(fill="x", pady=10, side="top")

        slide_bar.pack(fill="x", side="top")

        slide_bar_F.pack(fill="x", pady=10)

    def slider_command(self, event, title, value_label):
        value_label.configure(text = f"{int(event)}")
        if title == "Volume":
            self.SNFY_C_Class.volume_multiplier = int(event)/10
        elif title == "Time (s)":
            self.SNFY_C_Class.recalculate(int(event))

    def insert_data(self, home_image=None):
        self.img_saved_copy = Image.open(self.Snfy_img_path) if home_image == None else home_image #to be saved later on
        self.img_open= Image.open(self.Snfy_img_path) if home_image == None else home_image
        self.menu_page_frame.pages_dict["Add"].home_image = None

        self.img_w, self.img_h = self.img_open.size
        self.img_cnvs_frm.update()
        self.cnvsw, self.cnvsh = (self.img_cnvs_frm.winfo_width(), self.img_cnvs_frm.winfo_height())
        cnvs_ratio = self.cnvsw/self.cnvsh
        self.img_ratio = self.img_w/self.img_h
        self.img_open= self.img_open.resize(( int(self.cnvsw) , int(self.cnvsw/(self.img_w/self.img_h)) ) if cnvs_ratio <= self.img_ratio else ( int(self.cnvsh*(self.img_w/self.img_h)) , int(self.cnvsh) ))
        self.img_tk  = ImageTk.PhotoImage(self.img_open)
        self.image_canvas.create_image(int(self.cnvsw/2), int(self.cnvsh/2), image=self.img_tk, anchor="center", tag="snfy_img")


        self.S_size = self.analization_output[1]
        self.S_notes = self.analization_output[2]
        self.S_volume = self.analization_output[3]
        if self.analization_output[0] == "Opened":
            self.S_audio_full_time = self.analization_output[4]
            self.S_pixel_time      = self.analization_output[5]
        else:
            self.S_audio_full_time = self.t_slider_default
            self.S_pixel_time      = None

        self.SNFY_C_Class = F2_Sonify.SCommands(self, self.S_size, self.S_notes, self.S_volume, self.S_audio_full_time, self.S_pixel_time, None if self.v_slider_default == None else self.v_slider_default)

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")
        self.save_d = ctk.CTkButton(self.tools_f, text="", fg_color="transparent", hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")), image=ctk.CTkImage(Image.open(f"images/Icons/save_b.png"), Image.open(f"images/Icons/save_w.png"), (30, 30)), command = self.save_btn_func)
        self.save_d.pack(ipadx = 10, pady=10)

    def save_btn_func(self):
        folder_path = filedialog.askdirectory( initialdir = os.path.join(os.path.expanduser('~'), 'Desktop'),
                                                title = "Select a Folder",)
        if folder_path == "":
            folder_path = None
        else:
            self.SNFY_C_Class.save_data(folder_path, self.img_saved_copy)


