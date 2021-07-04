from simple_image_download import simple_image_download
import multiprocessing
from names import names


# A better way of doing this would be to use the face_recognition to identify all the faces and make sure there aren't multiple faces in a single image
# Todo: Add checks for faces also match against a sample image
def main():
    response = simple_image_download()

    for name in names:
        t1 = multiprocessing.Process(target=response.download, args=(
            name, name, 200, {'.jpg', '.png', '.jiff', '.gif', '.jpeg'}))
        t2 = multiprocessing.Process(target=response.download, args=(
            name + " face", name, 200, {'.jpg', '.png', '.jiff', '.gif', '.jpeg'}, True))

        t1.start()
        t2.start()

        # t1.join()
        # t2.join()


if __name__ == '__main__':
    main()
