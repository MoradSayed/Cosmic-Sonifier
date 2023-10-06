import os
import time

import numpy as np
from PIL import Image


# _____________________________________________ # 
# | --> direction of image data               | # 
# |                                           | # 
# |                                           | # 
# |                                           | # 
# |                   Morad                   | # 
# |                                           | # 
# |                                           | # 
# |                                           | # 
# _____________________________________________ # 

class Sonify:
    def __init__(self, image=None, image_path=None, return_queue=None):
        self.image_path = image_path

        self.im   = Image.open(self.image_path) if image == None else image
        self.im_g = self.im.convert('L')
        self.width, self.height = (self.im.size)

        self.start_time = time.time()        # start time of the program

        self.brightness  = self.get_brightness()
        self.im_g_mapped = self.brightness[0]
        self.im_g_pitch  = self.brightness[1]

        self.notes = self.get_notes()

        self.end_time = time.time()          # end time of the program

        self.Analizing_time = self.end_time - self.start_time
        # print("Analizing time:", self.Analizing_time)

        # self.sonification = MIDI(size=(self.width, self.height), notes=self.notes, volume=self.im_g_mapped)
        return_queue.put(self.return_function())

    def rgb_to_rainbow_color_vectorized(self, rgb_values):
        # Define the rainbow colors
        rainbow_colors = {
            'C': (255, 0  , 0  ),   # Red
            'D': (255, 255, 0  ), # Yellow
            'E': (0  , 225, 0  ),   # Green
            'F': (0  , 255, 255), # Cyan
            'G': (0  , 0  , 255),   # Blue
            'A': (255, 0  , 255)  # Violet
        }

        # Define the RGB ranges for white and black
        white_range = ((240, 240, 240), (255, 255, 255))
        black_range = ((0, 0, 0), (15, 15, 15))

        # Check if the RGB values fall within the white or black range
        is_white = np.all((white_range[0] <= rgb_values) & (rgb_values <= white_range[1]), axis=2)  # array of booleans (True if white)
        is_black = np.all((black_range[0] <= rgb_values) & (rgb_values <= black_range[1]), axis=2)  # array of booleans (True if black)
        
        # Create an array of shape (height, width) to store the closest color
        closest_color = np.empty(rgb_values.shape[:2], dtype='U1')  # empty array of strings
        min_distances = np.inf * np.ones(rgb_values.shape[:2])      # array of infinities
        
        # Calculate the Euclidean distances for rainbow colors and find the closest color
        for color, rgb in rainbow_colors.items():
            distances = np.linalg.norm(rgb_values - rgb, axis=2)    # array of Euclidean distances
            update_mask = distances < min_distances                 # array of booleans (True if the distance is less than the minimum distance)
            closest_color[update_mask] = color                      # update the closest color where the update mask is True
            min_distances[update_mask] = distances[update_mask]     # update the minimum distance where the update mask is True
        
        # Set 'B' for white and 'C' for black
        closest_color[is_white] = 'B'   # overrides the closest color if it is white      ##########################
        closest_color[is_black] = 'C'   # overrides the closest color if it is black      ########################## 
        
        return closest_color

    def get_brightness(self):
        im_g_data = np.array(list(self.im_g.getdata()))  # grayscale data extracted from the grayscaled image

        im_g_result_org = im_g_data.reshape(self.height, self.width)

        im_g_mapped = (im_g_result_org)/255

        conditions = [
            (im_g_mapped >= 0)  & (im_g_mapped <= 0.1),
            (im_g_mapped > 0.1) & (im_g_mapped <= 0.4),
            (im_g_mapped > 0.4) & (im_g_mapped <= 0.7),
            (im_g_mapped > 0.7) & (im_g_mapped <= 1)
        ]

        choices = [2, 3, 4, 5]

        # conditions = [
        #     (im_g_mapped >= 0)  & (im_g_mapped <= 0.2),
        #     (im_g_mapped > 0.2) & (im_g_mapped <= 0.6),
        #     (im_g_mapped > 0.6) & (im_g_mapped <= 1)
        # ]

        # choices = [2, 3, 4]

        im_g_pitch = np.select(conditions, choices, default=0).astype(str)

        # print(im_g_data)        # rgb data extracted from the original image
        # print(im_g_result_org)  # organized brightness values array
        # print(im_g_mapped)      # mapped brightness values array, 0 --> 1
        # print(im_g_pitch)       # note number array, created based on the brightness values
        
        return (im_g_mapped, im_g_pitch)

    def get_notes(self):
        im_data   = np.array(list(self.im.getdata())).reshape(self.height, self.width, 3)    # rgb data extracted from the original image

        im_result_org = self.rgb_to_rainbow_color_vectorized(im_data)
        im_result_org = np.char.add(im_result_org, self.im_g_pitch)

        # np.savetxt('test1.txt', im_result_org, fmt='%s') # save data to a text file

        # print(im_data)      # rgb data extracted from the original image
        # print(im_result_org)# organized note names array

        return im_result_org

    def return_function(self):
        # print(self.notes, self.im_g_mapped)
        return ["New", (self.width, self.height), self.notes, self.im_g_mapped]

# Gradual Transition: Create a gradual transition between pitch and volume levels as brightness values change. 
# You might use linear or logarithmic mappings to ensure that changes in brightness are reflected smoothly in pitch and volume changes.