
import threading
import face_recognition
import os
import pickle
import progressbar


bar = progressbar.ProgressBar(maxval=100,
                              widgets=[progressbar.Bar('⬛', '[', ']', '⬜'), ' ', progressbar.Percentage()]).start()


class Populate():
    def __init__(self) -> None:
        self.known_faces = []
        self.known_names = []
        self.KNOWN_FACES_DIR = "Images/Known"

    def loadImages(self):
        print("\n")
        print("Loading known faces")

        if os.path.exists("names.txt"):
            with open("names.txt", 'r') as raw_data:
                data = str(raw_data.read())
                if len(data) > 5:
                    data = eval(data)
                    self.known_names = data
                    with open('faces.dat', 'rb') as f:
                        self.known_faces = pickle.load(f)
                    print("Done loading known faces...")
                else:
                    print("No known faces found")
                    print("Populating data...")
                    self.loadFaces()
        else:
            print("No known faces found")
            print("Populating data...")
            self.loadFaces()

    def loadFaces(self):
        self.count = sum([len(files)
                          for r, d, files in os.walk("Images/Known")])
        # with alive_bar(self.count) as bar:
        bar.maxval = self.count
        for name in os.listdir(self.KNOWN_FACES_DIR):

            threads = [threading.Thread(target=self.resolveImages,
                                        args=(name, filename)) for filename in os.listdir(f"{self.KNOWN_FACES_DIR}/{name}")]

            for thread in threads:
                thread.start()
                thread.join()
        self.save()

    def resolveImages(self, name, filename):

        image = face_recognition.load_image_file(
            f"{self.KNOWN_FACES_DIR}/{name}/{filename}")
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            encoding = encodings[0]
            self.known_faces.append(encoding)
            self.known_names.append(name)

        bar.update(value=bar.currval+1)
        self.save()

    def save(self):
        with open('faces.dat', 'wb') as f:
            pickle.dump(self.known_faces, f)
        open("names.txt", 'w+').write(str(self.known_names))
