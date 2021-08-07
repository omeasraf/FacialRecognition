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
    def __init__(self, master=None, show_original: bool = False, known_faces=None, known_names=None):
        super().__init__(master)
        if known_names is None:
            known_names = []
        if known_faces is None:
            known_faces = []
        self.master = master
        self.master.configure(background='#282a35')
        self.master.minsize(500, 400)
        self.show_original = show_original
        self.master.title("Face Recognition")
        self.known_faces = known_faces
        self.known_names = known_names

        self.tolerance = 0.5
        self.FRAME_THICKNESS = 3
        self.MODEL = "hog"  # cnn
        self.originalImage = None
        self.identifiedImage = None
        self.saveImageButton = None
        self.container = tk.Frame(background='#282a35', width=200, height=70)
        self.container.pack(pady=5)
        self.container.pack_propagate(False)

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        pickImage = tk.Button(master=self.container, text="Pick Image", command=self.select_image, bg="white", fg='#282a35')
        pickImage.pack(pady=5)
        quitButton = tk.Button(master=self.container, text="Exit", fg="red",
                               command=self.master.destroy)
        quitButton.pack(side="bottom", padx=6)

        container = tk.Frame(background="#282a35", width=200, height=60)
        container.pack(pady=5)
        defaultValue = tk.StringVar(container)
        textLabel = tk.Label(container, text="Tolerance: ")
        self.spinBox = tk.Spinbox(
            container, from_=0, to=10, values=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            command=self.assignTolerance, textvariable=defaultValue)
        textLabel.configure(foreground="white", bg='#282a35')
        desc_label = tk.Label(container, text="Lower is better")
        desc_label.configure(foreground="white", bg='#282a35')
        desc_label.pack(side=tk.RIGHT, padx=5)
        self.spinBox.pack(side=tk.RIGHT)
        textLabel.pack(side=tk.LEFT, padx=5)

        defaultValue.set(str(self.tolerance))

    def assignTolerance(self):
        self.tolerance = float(self.spinBox.get())

    def select_image(self):

        filename = askopenfilename(filetypes=(
            ('all files', '.*'),
            ('image files', '.png'),
            ('image files', '.jpg'),))
        if len(filename) > 0:
            if self.show_original:
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
                    # Todo: print(f"Confidence Level: {}")
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
                    font_scale = (img_size[0] * img_size[1]) / (1000 * 1000)
                    font_scale = 0.5 if font_scale < 0.5 else font_scale
                    font_scale = 3 if font_scale > 10 else font_scale

                    font_thickness = 3 if font_scale >= 2 else 1

                    cv2.putText(image, match, (face_location[3] + 5, face_location[2] + 35),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)
                    pil_img = Image.fromarray(image)
                    width, height = pil_img.size
                    pil_img = pil_img.resize(
                        (round(680 / height * width), round(680)))

                    img = ImageTk.PhotoImage(pil_img)
                    if self.identifiedImage is None:
                        self.identifiedImage = tk.Label(image=img)
                        self.identifiedImage.image = img
                        self.identifiedImage.pack(
                            side="bottom", padx=10, pady=10)

                    else:
                        self.identifiedImage.configure(image=img)
                        self.identifiedImage.image = img

                    if self.saveImageButton is None:
                        self.container.config(height=110)
                        self.saveImageButton = tk.Button(
                            self.container, text="Save Image", command=lambda: self.saveImage(pil_img, filename))
                        self.saveImageButton.pack(
                            side="bottom", padx=6, pady=10)
                    else:
                        self.saveImageButton.configure(
                            command=lambda: self.saveImage(pil_img, filename))
            if not matchFound:
                tk.messagebox.showerror("Error", "No matches found")
        else:
            tk.messagebox.showerror(
                "Error", "Database is empty! did you forget to populate the database?")

    def saveImage(self, image: Image, file_name):
        print("Saving image")
        image.save(".".join(file_name.split(".")[
                            0:-1]) + "-identified." + file_name.split(".")[-1])
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
    root["bg"] = "#282a35"
    root.configure(background="#282a35")
    app = RecognizeFace(
        master=root, known_faces=populate.known_faces, known_names=populate.known_names)
    app.mainloop()
