import os
import face_recognition
import progressbar
import pickle
import multiprocessing
import numpy as np
import threading


class Generate:
    """
    Used for creating segmented facial data.
    A new dataset is created for each person


    Attributes
    ----------
    KNOWN_FACES_DIR : str
        Path to known faces directory
    known_faces : List
        Used for storing all the encoded data
    known_names : List
        Used for storing all the name data

    FUNCTIONS
    ----------
    resolve -> Void
        Initiates the resolve function
    resolve_images -> Void
        Resolves all the images in the known faces directory
    save -> Void
        Saves the data to a pickle file
    """

    def __init__(self) -> None:
        self.KNOWN_FACES_DIR = "Images/Known"
        self.known_faces = []
        self.known_names = []

    def resolve(self, name, dirname):
        count = sum([len(files)
                     for r, d, files in os.walk(f"{self.KNOWN_FACES_DIR}/{name}")])
        bar = progressbar.ProgressBar(maxval=count,
                                      widgets=[progressbar.Bar('⬛', '[', ']', '⬜'), ' ', progressbar.Percentage()]).start()
        dir_list = os.listdir(f"{self.KNOWN_FACES_DIR}/{name}")
        arr = np.array(dir_list)
        newarr = np.array_split(arr, 120)
        threads = [threading.Thread(
            target=self.resolve_images, args=[arr, name, bar, dirname]) for arr in newarr]
        for thread in threads:
            thread.start()
            thread.join()
        self.save(dirname)

        bar.finish()

    def resolve_images(self, arr, name, bar, dirname):
        for filename in arr:
            image = face_recognition.load_image_file(
                f"{self.KNOWN_FACES_DIR}/{name}/{filename}")
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                encoding = encodings[0]
                self.known_faces.append(encoding)
                self.known_names.append(name)
            bar.update(value=bar.currval+1)
        self.save(dirname)

    def save(self, dirname):
        if not os.path.isdir("dataset"):
            os.makedirs("dataset")
        if not os.path.isdir(f"dataset/{str(dirname)}"):
            os.makedirs(f'dataset/{str(dirname)}')
        with open(f'dataset/{str(dirname)}/faces.dat', 'wb') as f:
            pickle.dump(self.known_faces, f)
        open(f"dataset/{str(dirname)}/names.txt",
             'w+').write(str(self.known_names))


def main():
    print("Initiating all processes...")
    dir_list = os.listdir("Images/Known")
    arr = np.array(dir_list)
    newarr = np.array_split(arr, 35)

    for arr in newarr:
        gen = Generate()
        thread = multiprocessing.Process(
            target=res, args=[arr, gen])
        thread.start()
        # thread.join()


def res(arr, gen):
    threads = [multiprocessing.Process(target=gen.resolve, args=[name, name])
               for name in arr]
    for thread in threads:
        thread.start()
        thread.join()


if __name__ == "__main__":
    main()
