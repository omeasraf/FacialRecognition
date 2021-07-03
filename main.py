from populateData import Populate
import face_recognition
import os
import cv2
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from populateData import Populate
import time
from PIL import Image
from PIL import ImageTk
import threading


class RecognizeFace(tk.Frame):
    def __init__(self, master=None, showOriginal: bool = False, known_faces=[], known_names=[]):
        super().__init__(master)
        self.master = master
        self.master.minsize(500, 400)
        self.showOriginal = showOriginal
        self.master.title("Face Recognition")
        self.pack()
        self.create_widgets()
        self.known_faces = known_faces
        self.known_names = known_names

        self.TOLERANCE = 0.3
        self.FRAME_THICKNESS = 3
        self.FONT_THICKNESS = 1
        self.MODEL = "hog"  # cnn
        self.originalImage = None
        self.identifiedImage = None
        self.saveImageButton = None

    def create_widgets(self):

        # self.loadButton = tk.Button(self, command=threading.Thread(
        #     target=self.loadImages).start())
        # self.loadButton["text"] = "Populate Database"
        # self.loadButton.pack(side="top")

        self.pickImage = tk.Button(self)
        self.pickImage["text"] = "Pick Image"
        self.pickImage["command"] = self.select_image
        self.pickImage.pack(side="top", padx=6, pady=10)

        self.quitButton = tk.Button(self, text="Exit", fg="red",
                                    command=self.master.destroy)
        self.quitButton.pack(side="bottom", padx=6, pady=10)

    def select_image(self):

        filename = askopenfilename(filetypes=(
            ('all files', '.*'),
            ('text files', '.txt'),
            ('image files', '.png'),
            ('image files', '.jpg'),))
        if len(filename) > 0:
            if self.showOriginal:
                img = ImageTk.PhotoImage(file=filename)
                if self.originalImage is None:
                    self.originalImage = tk.Label(image=img)
                    self.originalImage.image = img
                    self.originalImage.pack(side="left", padx=10, pady=10)
                else:
                    self.originalImage.configure(image=img)
                    self.originalImage.image = img
            self.master.update()
            threading.Thread(target=self.loadUnknownFace(filename)).start()

    def loadImages(self):
        print("Loading known faces")

        if os.path.exists("names.txt"):
            with open("names.txt", 'r') as raw_data:
                data = str(raw_data.read())
                if len(data) > 5:
                    data = eval(data)
                    self.known_names = data
                    with open('faces.dat', 'rb') as f:
                        self.known_faces = pickle.load(f)
                else:
                    self.loadFaces()
        else:
            self.loadFaces()

        print("Done loading images")

    def loadUnknownFace(self, filename):
        if len(self.known_names) > 0:
            print("Processing unknown faces")
            print(f"{str(len(self.known_faces))} cached image(s) found")
            image = face_recognition.load_image_file(filename)
            locations = face_recognition.face_locations(
                image, model=self.MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            matchFound: bool = False
            for face_encoding, face_location in zip(encodings, locations):
                results = face_recognition.compare_faces(
                    self.known_faces, face_encoding, self.TOLERANCE)
                match = None
                if True in results:
                    matchFound = True
                    match = self.known_names[results.index(True)]
                    print(f"Match Found: {match}")
                    # top, right, bottom, left = face_location
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])
                    color = [93, 245, 66]
                    cv2.rectangle(image, top_left, bottom_right,
                                  color, self.FRAME_THICKNESS)
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 22)
                    cv2.rectangle(image, top_left, bottom_right,
                                  color, cv2.FILLED)
                    cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), self.FONT_THICKNESS)
                    pilImg = Image.fromarray(image)
                    width, height = pilImg.size
                    pilImg = pilImg.resize(
                        (round(680/height*width), round(680)))

                    img = ImageTk.PhotoImage(pilImg)
                    if self.identifiedImage is None:
                        self.identifiedImage = tk.Label(image=img)
                        self.identifiedImage.image = img
                        self.identifiedImage.pack(
                            side="right", padx=10, pady=10)

                    else:
                        self.identifiedImage.configure(image=img)
                        self.identifiedImage.image = img
                    self.saveImageButton = tk.Button(
                        self, text="Save Image", command=lambda: self.saveImage(pilImg, filename))
                    self.saveImageButton.pack(side="bottom", padx=6, pady=10)
            if matchFound == False:
                tk.messagebox.showerror("Error", "No matches found")
        else:
            tk.messagebox.showerror(
                "Error", "Database is empty! did you forget to populate the database?")

    def saveImage(self, image, fileName):
        print("Saving image")
        image.save(".".join(fileName.split(".")[
                   0:-1]) + "-identified." + fileName.split(".")[-1])
        tk.messagebox.showinfo(
            "Success", "Successfully saved the image to the origial directory!")


if __name__ == '__main__':

    time.sleep(1)
    populate = Populate()
    populate.loadImages()
    print("Done populating...")
    root = tk.Tk()
    app = RecognizeFace(
        master=root, known_faces=populate.known_faces, known_names=populate.known_names)
    app.mainloop()
