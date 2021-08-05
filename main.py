from populateData import Populate
import face_recognition
import cv2
import tkinter as tk
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
        self.known_faces = known_faces
        self.known_names = known_names

        self.tolerance = 0.5
        self.FRAME_THICKNESS = 3
        self.MODEL = "hog"  # cnn
        self.originalImage = None
        self.identifiedImage = None
        self.saveImageButton = None

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.pickImage = tk.Button(self)
        self.pickImage["text"] = "Pick Image"
        self.pickImage["command"] = self.select_image
        self.pickImage.pack(side="top", padx=6, pady=10)

        self.quitButton = tk.Button(self, text="Exit", fg="red",
                                    command=self.master.destroy)
        self.quitButton.pack(side="bottom", padx=6, pady=10)

        defaultValue = tk.StringVar(self.master)
        textLabel = tk.Label(self.master, text="Tolerance: ")
        #Todo: descLabel = tk.Label(self.master, text="Lower is better...")
        self.spinBox = tk.Spinbox(
            self.master, from_=0, to=10, values=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], command=self.assignTolerance, textvariable=defaultValue)
        textLabel.pack(padx=6, pady=10)
        self.spinBox.pack(padx=6, pady=10)
        # self.spinBox.place(x=150, y=130)
        defaultValue.set(str(self.tolerance))
        # descLabel.pack(side="top", padx=6, pady=10, expand=tk.YES)

    def assignTolerance(self):
        self.tolerance = float(self.spinBox.get())

    def select_image(self):

        filename = askopenfilename(filetypes=(
            ('all files', '.*'),
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
            threading.Thread(target=self.load_unknown_face(filename)).start()

    def load_unknown_face(self, filename):
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
                    self.known_faces, face_encoding, self.tolerance)
                match = None
                if True in results:
                    matchFound = True
                    match = self.known_names[results.index(True)]
                    print(f"Match Found: {match}")
                    # print(f"Confidence Level: {}")
                    # top, right, bottom, left = face_location
                    top_left = (face_location[3], face_location[0])
                    bottom_right = (face_location[1], face_location[2])
                    color = [93, 245, 66]
                    cv2.rectangle(image, top_left, bottom_right,
                                  color, self.FRAME_THICKNESS)
                    top_left = (face_location[3], face_location[2])
                    bottom_right = (face_location[1], face_location[2] + 40)
                    cv2.rectangle(image, top_left, bottom_right,
                                  color, cv2.FILLED)

                    img_size = image.shape[1::-1]
                    font_scale = (img_size[0] * img_size[1])/(1000 * 1000)
                    font_scale = 0.5 if font_scale < 0.5 else font_scale
                    font_scale = 3 if font_scale > 10 else font_scale

                    font_thickness = 3 if font_scale >= 2 else 1

                    cv2.putText(image, match, (face_location[3], face_location[2] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)
                    print(font_scale)
                    pilImg = Image.fromarray(image)
                    width, height = pilImg.size
                    pilImg = pilImg.resize(
                        (round(680/height*width), round(680)))

                    img = ImageTk.PhotoImage(pilImg)
                    if self.identifiedImage is None:
                        self.identifiedImage = tk.Label(image=img)
                        self.identifiedImage.image = img
                        self.identifiedImage.pack(
                            side="bottom", padx=10, pady=10)

                    else:
                        self.identifiedImage.configure(image=img)
                        self.identifiedImage.image = img

                    if self.saveImageButton is None:
                        self.saveImageButton = tk.Button(
                            self, text="Save Image", command=lambda: self.saveImage(pilImg, filename))
                        self.saveImageButton.pack(
                            side="bottom", padx=6, pady=10)
                    else:
                        self.saveImageButton.configure(
                            command=lambda: self.saveImage(pilImg, filename))
            if not matchFound:
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
    # populate.load_images()  # Use this to populate the dataset from a dataset/ directory
    # Use this to populate the dataset from all subdirectories of dataset/
    populate.load_all_images()
    print("Done populating...")
    root = tk.Tk()
    app = RecognizeFace(
        master=root, known_faces=populate.known_faces, known_names=populate.known_names)
    app.mainloop()
