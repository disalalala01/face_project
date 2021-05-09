import face_recognition
import cv2
import numpy as np
import time
import tkinter as tk
from PIL import ImageTk, Image
import glob
import os

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
        cv2.destroyAllWindows()
    
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
        

class RecognitionPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.vid = MyVideoCapture(0)
        self.canvas = tk.Canvas(self, width = self.vid.width, height = self.vid.height)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        self.face_rec = FaceRecognition()
        tk.Label(self, 
                text="Идет распознование...", 
                font=('Helvetica', 18, "bold")) \
                    .place(relx=0.5, rely=0.1, anchor="center")
        tk.Button(self, 
                text="Главное меню",
                command=lambda: self.close_and_back(master)) \
                    .place(x=0, rely=1.0, anchor="sw", width=120)
        
        self.delay = 15
        self.task = self.after(self.delay, self.update)
        self.snapshot_taken = False

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            res_frame = self.face_rec.find_faces(frame)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(res_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        if not self.snapshot_taken:
            self.task = self.after(self.delay, self.update)

    def get_face_locations(self, frame):
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        return face_locations

    def close_and_back(self, master):
        from main import StartPage
        del self.vid
        master.switch_frame(StartPage)


class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.fill_encodings()
        self.process_order = 5
        self.face_names = []
        self.face_locations = []

    def fill_encodings(self):
        namelist = [i for i in glob.glob("./people/*jpg")]
        for fname in namelist:
            known_name = fname[fname.rindex('/') + 1:fname.rindex('.')]
            known_face = face_recognition.load_image_file(fname)
            known_encoding = face_recognition.face_encodings(known_face)[0]
            self.known_face_names.append(known_name)
            self.known_face_encodings.append(known_encoding)

    def find_faces(self, frame, process=False):
        if self.process_order == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            self.face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, self.face_locations)
            self.face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = -1
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                if best_match_index >= 0 and matches[best_match_index] and face_distances[best_match_index] < 0.3:
                    name = self.known_face_names[best_match_index]

                self.face_names.append(name)
            self.process_order = 5

        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        self.process_order -= 1
        return frame
