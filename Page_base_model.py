import tkinter as tk

import customtkinter as ctk

from Theme import *


class Page_BM(ctk.CTkFrame): #the final frame to use is the "self.Scrollable_frame"
    def __init__(self, window, parent, scrollable=True):
        super().__init__(parent, fg_color="transparent")
        self.window = window
        self.parent = parent
        self.scrollable = scrollable
        self.started = False    # to check if the page is opened for the first time or not

        if self.scrollable:
            self.Scrollable_canvas = tk.Canvas(self, background=LIGHT_MODE["background"] if ctk.get_appearance_mode() == "Light" else DARK_MODE["background"], scrollregion = (0, 0, self.winfo_width(), 10000), bd=0, highlightthickness=0, relief = 'ridge')
            self.Scrollable_canvas.pack(fill="both", expand=True)
            self.Scrollable_frame = ctk.CTkFrame(self.Scrollable_canvas, fg_color="transparent", bg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
        else:
            self.Scrollable_frame = ctk.CTkFrame(self, fg_color="transparent", bg_color=(LIGHT_MODE["background"], DARK_MODE["background"]))
            self.Scrollable_frame.pack(fill="both", expand=True)


    def called_when_opened(self):
        if self.scrollable:
            # draw_scrollable_frame
            self.update()
            self.Scrollable_canvas.create_window(                                                       #we create it with a large height to see where is the last widget
                (0,0), 
                window=self.Scrollable_frame, 
                anchor="nw", 
                width = self.winfo_width(), 
                height = 10000, 
                tags= "frame")
            
            self.update()
            self.max_height = self.Scrollable_frame.winfo_children()[-1].winfo_y()                      # then we get the y position of the last widget

            self.Scrollable_canvas.configure(scrollregion=(0, 0, self.winfo_width(), self.max_height))  # then we set the scrollable region to the last widget y position
            # there is no need to edit the frame height, just leave it with its default height, and limit the scroll using the canvas only
            
            if self.max_height > self.winfo_height():                                                   # if the max height is bigger than the frame height, we add the scrollbar
                self.Scrollable_canvas.bind_all("<MouseWheel>", lambda event: self.Scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            else:
                self.Scrollable_canvas.unbind_all("<MouseWheel>")

        if self.started == False:
            self.started = True
            self.on_start() # this function is called only once when the page is opened for the first time

        self.on_pick()      # this function is called every time the page is opened


    def update_size_BM(self):
        if self.scrollable:
            self.update()
            self.Scrollable_canvas.itemconfigure("frame", width=self.winfo_width())
            
            if self.max_height > self.winfo_height():                                                   # if the max height is bigger than the frame height, we add the scrollbar
                self.Scrollable_canvas.bind_all("<MouseWheel>", lambda event: self.Scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            else:
                self.Scrollable_canvas.unbind_all("<MouseWheel>")
            
        self.on_update()    # this function is called every time the page is resized
    