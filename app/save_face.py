import face_recognition
import cv2
import numpy as np
import time
import tkinter as tk
from PIL import ImageTk, Image
import glob
import os
from face_rec import MyVideoCapture


class AddFacePage(tk.Frame):
    
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.vid = MyVideoCapture(0)
        self.canvas = tk.Canvas(self, 
                    width = self.vid.width - 50, 
                    height = self.vid.height - 50,
                    highlightthickness=10)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self, 
                text="Добавить новое лицо", 
                font=('Helvetica', 18, "bold")) \
                    .place(relx=0.5, rely=0.1, anchor="center")
        tk.Button(self, 
                text="Назад",
                command=lambda: self.close_and_back(master)) \
                    .place(x=0, rely=1.0, anchor="sw", width=120)
        tk.Button(self, 
                text="Сделать снимок",
                command=self.snapshot) \
                    .place(relx=0.5, rely=0.9, anchor="s", width=200)
        
        self.delay = 15
        self.task = self.after(self.delay, self.update)
        self.snapshot_taken = False

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            face_locations = self.get_face_locations(frame)
            if len(face_locations) == 1:
                color, can_capture = '#%02x%02x%02x' % (0, 255, 0), True
            else:
                color, can_capture = '#%02x%02x%02x' % (255, 0, 0), False
            
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.config(highlightbackground=color)
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        if not self.snapshot_taken:
            self.task = self.after(self.delay, self.update)


    def snapshot(self):
        self.snapshot_taken = True
        ret, frame = self.vid.get_frame()
        if ret:
            top, right, bottom, left = self.get_face_locations(frame)[0]
            crop_frame = frame[top - 100: bottom + 50, left - 50:right + 50]
            self.after_cancel(self.task)
            del self.vid
            self.master.switch_frame(SaveFacePage, frame=crop_frame)


    def get_face_locations(self, frame):
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        return face_locations

    def close_and_back(self, master):
        from main import FacesPage
        del self.vid
        master.switch_frame(FacesPage)


class SaveFacePage(tk.Frame):
    def __init__(self, master, frame):
        tk.Frame.__init__(self, master)
        self.canvas = tk.Canvas(self, 
                    width = 400, 
                    height = 400)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self, 
                text="Добавить новое лицо", 
                font=('Helvetica', 18, "bold")) \
                    .place(relx=0.5, rely=0.1, anchor="center")
        tk.Button(self, 
                text="Назад",
                command=lambda: self.close_and_back(master)) \
                    .place(x=0, rely=1.0, anchor="sw", width=120)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.canvas.create_image(200, 200, image=self.photo, anchor="center")
        self.entry_name = tk.Entry(self)
        self.name_label = tk.Label(self, text="Введите имя")
        self.name_label.place(relx=0.5, rely=0.8, anchor="s")
        self.entry_name.place(relx=0.5, rely=0.85, anchor="s")
        tk.Button(self, 
                text="Сохранить",
                command=lambda: self.save_image_and_close(frame)) \
                    .place(relx=0.5, rely=0.9, anchor="s", width=120)

    def close_and_back(self, master):
        master.switch_frame(AddFacePage)

    def save_image_and_close(self, frame):
        file_name = self.entry_name.get() + ".jpg"
        file_path = os.path.join('people', file_name)
        Image.fromarray(frame).save(file_path)
        from main import FacesPage
        self.master.switch_frame(FacesPage)