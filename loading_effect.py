import os, time

import customtkinter as ctk
from PIL import Image

from Theme import *
from utils import hvr_clr_g


class load_ing(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.parent = parent
        self.image_list = []
        self.img_frame_counter = 0
        
        self.state = "off"
        self.packed = False

        self.folder_path_w = os.path.join("images", "Loading", "astro_w")
        self.folder_path_b = os.path.join("images", "Loading", "astro_b")
        for i in range(300):
            w = Image.open(os.path.join(self.folder_path_w, f"{i}.png"))
            b = Image.open(os.path.join(self.folder_path_b, f"{i}.png"))
            img = ctk.CTkImage(light_image=b, dark_image=w, size=(100, 100))
            self.image_list.append(img)

        self.loading_btn = ctk.CTkButton(self, text="", fg_color="transparent", bg_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")),
                                         hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")),
                                         height=250, width=250, image=self.image_list[self.img_frame_counter])
        self.pack(expand=True, fill="both")

    def start(self):
        if self.state == "off":
            self.state = "on"
            self.loading_btn.pack(expand=True, fill="y")
            self.packed = True
            self.load_animation()

    def load_animation(self):
        # print(self.state == "on", self.packed == True)
        if self.state == "on" and self.packed == True:
            self.img_frame_counter += 1
            self.loading_btn.configure(image=self.image_list[self.img_frame_counter])
            self.parent.update()
            if self.img_frame_counter == len(self.image_list)-1:
                self.img_frame_counter = -1

            self.after(16, self.load_animation)

    def stop(self):
        if self.state == "on":
            self.state = "off"
            self.loading_btn.pack_forget()
            self.packed = False
            self.img_frame_counter = -1
            # print("stopped")