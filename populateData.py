import os
import pickle


class Populate:
    def __init__(self) -> None:
        self.known_faces = []
        self.known_names = []
        self.KNOWN_FACES_DIR = "Images/Known"

    def loadImages(self):
        print("\n")
        print("Loading known faces")

        if not os.path.isdir("dataset"):
            os.makedirs("dataset")

        if os.path.exists("dataset/names.txt"):
            with open("dataset/names.txt", 'r') as raw_data:
                data = str(raw_data.read())
                if len(data) > 5:
                    data = eval(data)
                    self.known_names = data
                    with open('dataset/faces.dat', 'rb') as f:
                        self.known_faces = pickle.load(f)
                    print("Done loading known faces...")
                else:
                    print("No known faces found")
                    return None
        else:
            print("No known faces found")
            return None
