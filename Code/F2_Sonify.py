import datetime
import json
import os
import time
from tkinter import filedialog
from math import sqrt
import mido
import numpy as np
from mido import Message, MidiFile, MidiTrack, MetaMessage
from PIL import Image
from pyo import *
import numpy as np
import queue
import scipy.optimize as opt


MIDI_Note_Num = { "B5" : 83,  	
                  "A5" : 81,  	
                  "G5" : 79,  	
                  "F5" : 77,  	
                  "E5" : 76,  	
                  "D5" : 74,  	
                  "C5" : 72,  	
                  "B4" : 71,  	
                  "A4" : 69,    
                  "G4" : 67,  	
                  "F4" : 65,  	
                  "E4" : 64,  	
                  "D4" : 62,  	
                  "C4" : 60,    
                  "B3" : 59,  	
                  "A3" : 57,  	
                  "G3" : 55,  	
                  "F3" : 53,  	
                  "E3" : 52,  	
                  "D3" : 50,  	
                  "C3" : 48,  	
                  "B2" : 47,  	
                  "A2" : 45,  	
                  "G2" : 43,  	
                  "F2" : 41,  	
                  "E2" : 40,  	
                  "D2" : 38,  	
                  "C2" : 36  }

note_freqs = {
    "C2": 65.41 , # Hz 
    "D2": 73.42 , # Hz 
    "E2": 82.41 , # Hz 
    "F2": 87.31 , # Hz 
    "G2": 98.00 , # Hz 
    "A2": 110.00, # Hz 
    "B2": 123.47, # Hz 
    "C3": 130.81, # Hz 
    "D3": 146.83, # Hz 
    "E3": 164.81, # Hz 
    "F3": 174.61, # Hz 
    "G3": 196.00, # Hz 
    "A3": 220.00, # Hz 
    "B3": 246.94, # Hz 
    "C4": 261.63, # Hz 
    "D4": 293.66, # Hz 
    "E4": 329.63, # Hz 
    "F4": 349.23, # Hz 
    "G4": 392.00, # Hz 
    "A4": 440.00, # Hz 
    "B4": 493.88, # Hz 
    "C5": 523.25, # Hz 
    "D5": 587.33, # Hz 
    "E5": 659.26, # Hz 
    "F5": 698.46, # Hz 
    "G5": 783.99, # Hz 
    "A5": 880.00, # Hz 
    "B5": 987.77  # Hz 
}

miditohz = {
"36" : 65.41 ,
"38" : 73.42 ,
"40" : 82.41 ,
"41" : 87.31 ,
"43" : 98.00 ,
"45" : 110.00,
"47" : 123.47,
"48" : 130.81,
"50" : 146.83,
"52" : 164.81,
"53" : 174.61,
"55" : 196.00,
"57" : 220.00,
"59" : 246.94,
"60" : 261.63,
"62" : 293.66,
"64" : 329.63,
"65" : 349.23,
"67" : 392.00,
"69" : 440.00,
"71" : 493.88,
"72" : 523.25,
"74" : 587.33,
"76" : 659.26,
"77" : 698.46,
"79" : 783.99,
"81" : 880.00,
"83" : 987.77
}

class SCommands:
    def __init__(self, workspace, size, notes, volume, audio_full_time = 45, pixel_time = None, VM_input = None):
        self.midi_filename = "miditt_"
        self.wav_filename  =  "wav_"
        self.width  = size[0]
        self.height = size[1]
        self.size = self.width * self.height
        self.notes = notes
        self.volume = volume
        self.record = False
        self.workspace = workspace
        self.workshop_canvas = self.workspace.image_canvas


        self.volume_multiplier = 0.5 if VM_input == None else VM_input

        self.audio_full_time = audio_full_time # in secs (60 is preferred)
        self.pixels_per_beat = None if self.audio_full_time == None else int(self.height/self.audio_full_time)
        self.pixel_time = pixel_time if self.pixels_per_beat == None else (1/self.pixels_per_beat)  # in secs

        self.line_pos = queue.Queue()
        self.line_pos.put(self.workspace.cnvsh)
        self.line_thread = threading.Thread(target=self.draw_line, args=[self.line_pos,])
        self.line_thread.daemon = True
        self.line_thread.start()
    
    def create_MIDI(self):          # Method 1: midiutil
        # turn note name to MIDI number
        replacement_function = np.vectorize(lambda x: MIDI_Note_Num.get(x, x)) # Use np.vectorize to apply the function element-wise to the array, If key not in dictionary, keep the original key
        self.midi_num = replacement_function(self.notes)

        lowest_vol = 35
        highest_vol= 127
        self.MIDI_mapped_vol = (lowest_vol + (self.volume - 0)/(1 - 0)*(highest_vol - lowest_vol)).astype(int)
        # print(self.MIDI_mapped_vol)

        mid = MidiFile()
        # Create a new track
        track = MidiTrack()
        mid.tracks.append(track)

        # Set the tempo to 60 bpm (1,000,000 μs/beat)
        tempo = 1000000
        track.append(MetaMessage('set_tempo', tempo=tempo))
        ticks_per_beat = 480  # You might need to adjust this based on your MIDI file's resolution
        note_duration = self.pixel_time * ticks_per_beat * (tempo / 1_000_000)

        # Iterate through the arrays and add notes to the track
        for count, (freq_row, vol_row) in enumerate(zip(self.midi_num, self.MIDI_mapped_vol)):
            for freq, vol in zip(freq_row, vol_row):
                
                # Add a note-on message (start of the note)
                track.append(Message('note_on', note=freq, velocity=vol, time=int(note_duration * count)))
                
                # Add a note-off message (end of the note)
                track.append(Message('note_off', note=freq, velocity=vol, time=int(note_duration * (count+1))))

        # Save the MIDI file
        mid.save(f'output{datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")}.mid')

    def create_normal_pyo(self, continue_play):    # Method 2: pyo
        lock = 0

        replacement_function = np.vectorize(lambda x: note_freqs.get(x, x)) # Use np.vectorize to apply the function element-wise to the array, If key not in dictionary, keep the original key
        self.note_freq = replacement_function(self.notes)
        # print(self.note_freq, "\n\n", self.volume)
        
        s = Server().boot()
        s.start()
        # print("Server started")
        s.recordOptions(filename= os.path.join("Records", self.wav_filename + (datetime.datetime.now() + datetime.timedelta(minutes = self.pixel_time*self.size)).strftime("%d_%m_%Y_%H-%M-%S") + ".wav"))
        

        start_time = time.time()
        for num1, (freqs_1darray, vols_1darray) in enumerate(zip(self.note_freq, self.volume)): 
            self.workshop_image_height = self.workspace.cnvsh
            ratio = (self.workshop_image_height)/(self.note_freq.shape[0])
            if continue_play.queue[-1] == False:
                self.line_pos.put(self.workspace.cnvsh)
                break
            VM_checkpoint = self.volume_multiplier
            PT_checkpoint = self.pixel_time
            if lock == 0:
                lock = 1
                if self.record:
                    s.recstart()
                a = Sine(freq=list(freqs_1darray), mul=list(VM_checkpoint * ((vols_1darray/(self.width))**0.675)) ).out()
                time.sleep(PT_checkpoint)
                continue

            self.line_pos.put(int(num1*ratio))
            
            a.freq = list(freqs_1darray)
            a.mul  = list(VM_checkpoint * ((vols_1darray/(self.width))**0.675))
            time.sleep(PT_checkpoint)
        end_time = time.time()
        if self.record:
            s.recstop()
        playing_time = end_time - start_time
        # print("playing time:", playing_time)

        # s.gui(locals())
        s.stop()
        # print("Done")

    def draw_line(self,y_qu):
        checkpoint = None
        while True:
            y = y_qu.queue[-1]
            if checkpoint != y:
                checkpoint = y
                try:
                    self.workshop_canvas.delete("line")
                except:
                    pass
                self.workshop_canvas.create_line(0, y, self.workshop_canvas.winfo_width(), y, fill="white", width=1, tags="line")
            time.sleep(0.01)    

    def save_data(self, folder_path, the_image):
        np.savez(os.path.join(folder_path + '/Snfy_array.npz'), self.notes, self.volume)

        with open (os.path.join(folder_path + "/Snfy_pref.json"), "w") as f:
            json.dump({"size": [self.width, self.height], "audio_full_time": self.audio_full_time, "pixel_time": self.pixel_time}, f)

        the_image.save(os.path.join(folder_path + "/Snfy_img.jpg"))

    def play_MIDI_to_pyo(self, midi_file='midi_21_09_2023_21-21-04.mid'):
        lock = 0
        
        file_path = filedialog.askopenfilename( initialdir = os.path.join(os.path.expanduser('~'), 'Desktop'),
                                                title = "Select a File")

        st = time.time()
        mid = MidiFile(file_path)
        et = time.time() - st
        print("et:", et)
        # Initialize empty lists to store frequency and volume data
        frequencies = []
        volumes = []

        # Iterate through the MIDI messages in the first track
        for msg in mid.tracks[0]:
            if msg.type == 'note_on':
                frequencies.append(midiToHz(msg.note))
                volumes.append(self.volume_multiplier * (msg.velocity / 127.0)/(self.width*0.4))
        print("Step 2")

        # Convert the lists to NumPy arrays if needed
        frequencies = np.array(frequencies).reshape(self.height, self.width)
        volumes = np.array(volumes).reshape(self.height, self.width)
        print("Step 3")

        s = Server().boot()
        s.start()

        start_time = time.time()
        for num1, (freqs_1darray, vols_1darray) in enumerate(zip(frequencies, volumes)): 
            if lock == 0:
                lock = 1
                if self.record:
                    s.recstart()
                a = Sine(freq=list(freqs_1darray), mul=list(self.volume_multiplier * (vols_1darray/(self.width*0.4))) ).out()
                time.sleep(self.pixel_time)
                continue
            a.freq = list(freqs_1darray)
            a.mul  = list(self.volume_multiplier * (vols_1darray/(self.width*0.4)))
            time.sleep(self.pixel_time)
        end_time = time.time()
        if self.record:
            s.recstop()
        playing_time = end_time - start_time
        # print("playing time:", playing_time)

        # s.gui(locals())
        s.stop()

    def recalculate(self, full_time):
        self.pixels_per_beat = int(self.height/full_time)
        self.pixel_time = (1/self.pixels_per_beat)  # in secs

