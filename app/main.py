import tkinter as tk
from face_rec import MyVideoCapture
from PIL import ImageTk, Image
import glob
import os
import face_recognition
import cv2


class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = tk.Frame(self)
        self.geometry("800x700+300+300")
        self.title("Система Распознования Лиц")
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class, frame=None):
        if frame is None:
            new_frame = frame_class(self)
        else:
            new_frame = frame_class(self, frame)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=1)

class StartPage(tk.Frame):
    def __init__(self, master):
        from face_rec import RecognitionPage
        tk.Frame.__init__(self, master)
        
        tk.Label(self, 
                text="Система Распознования Лиц", 
                font=('Helvetica', 18, "bold")) \
                    .place(relx=0.5, rely=0.2, anchor="center")
        
        tk.Label(self, 
                text="by NAME_SURNAME", 
                font=('Helvetica', 11, "italic")) \
                    .place(relx=0.0, rely=1.0, anchor="sw")
        
        tk.Button(self, 
                text="Начать распознование", 
                command=lambda: master.switch_frame(RecognitionPage)) \
                    .place(relx=0.5, rely=0.5, anchor="center", width=200)

        tk.Button(self, 
                text="Все лица в базе",
                command=lambda: master.switch_frame(FacesPage)) \
                    .place(relx=0.5, rely=0.6, anchor="center", width=200)

        tk.Button(self,
                text="Выход", 
                command=self.quit) \
                    .place(relx=0.5, rely=0.7, anchor="center", width=200)


class FacesPage(tk.Frame):
    def __init__(self, master):
        from save_face import AddFacePage
        tk.Frame.__init__(self, master)
        tk.Label(self, 
                text="Лица в базе", 
                font=('Helvetica', 18, "bold")) \
                    .place(relx=0.5, rely=0.05, anchor="n")
        
        tk.Button(self, 
                text="Главное меню",
                command=lambda: master.switch_frame(StartPage)) \
                    .place(x=0, rely=1.0, anchor="sw", width=120)
        
        tk.Button(self, 
                text="+ Добавить",
                command=lambda: master.switch_frame(AddFacePage)) \
                    .place(x=120, rely=1.0, anchor="sw", width=100)
        
        tk.Button(self, 
                text="- Удалить",
                command=lambda: self.delete(master)) \
                    .place(x=220, rely=1.0, anchor="sw", width=100)
        

        self.lst = tk.Listbox(self)
        self.lst.pack(fill=tk.Y, expand=1, side="left", anchor="nw", pady=50, padx=10)
        namelist = [i for i in glob.glob("./people/*jpg")]
        for fname in namelist:
            self.lst.insert(tk.END, fname[fname.rindex('/') + 1:fname.rindex('.')])

        self.lst.bind("<<ListboxSelect>>", self.show)
        self.lab = tk.Label(self)
        self.lab.pack(side="left", padx=50)
        self.show(e=None)
        

    def show(self, e):
        if not e:
            self.lst.selection_set(0)
        if self.lst.size() > 0:
            n = self.lst.curselection()
            fname = f'./people/{self.lst.get(n)}.jpg'
            img = ImageTk.PhotoImage(Image.open(fname).resize((200, 200), Image.ANTIALIAS))
            self.lab.config(image=img)
            self.lab.image = img
    
    def delete(self, master):
        if self.lst.size() > 0:
            n = self.lst.curselection()
            fname = f'./people/{self.lst.get(n)}.jpg'
            os.remove(fname)
            master.switch_frame(FacesPage)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()