import face_recognition
import os

import cv2
import numpy as np
import pickle


# Constants
know_faces_dir = "Images/Known"
unknow_faces_dir = "Images/Unknown"
tolerance = 0.6
frame_thickness = 3
font_thicknewss = 2
MODEL = "hog" # cnn

print("Loading known faces")

known_faces = []
known_names = []


with open("names.txt") as raw_data:
    data = str(raw_data.read())
    if len(data) > 5:
        data = eval(data)
        known_names = data
        with open('faces.dat', 'rb') as f:
	        known_faces = pickle.load(f)
    else:    
        for name in os.listdir(know_faces_dir):
            for filename in os.listdir(f"{know_faces_dir}/{name}"):
                image = face_recognition.load_image_file(f"{know_faces_dir}/{name}/{filename}")
                encoding = face_recognition.face_encodings(image)[0]
                known_faces.append(encoding)
                known_names.append(name)   
        type(known_faces)
        with open('faces.dat', 'wb') as f:
            pickle.dump(known_faces, f)       
        open("names.txt", "w").write(str(known_names))

print("Processing unknown faces")
for filename in os.listdir(unknow_faces_dir):
    
    image = face_recognition.load_image_file(f"{unknow_faces_dir}/{filename}")
    locations = face_recognition.face_locations(image, model=MODEL)
    encodings = face_recognition.face_encodings(image, locations)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    
    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, tolerance)
        match = None
        if True in results:
            match = known_names[results.index(True)]
            print(f"Match Found: {match}")
            
            # top, right, bottom, left = face_location
            
            
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            color = [93, 245, 66]
            cv2.rectangle(image, top_left, bottom_right, color, frame_thickness)
            
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2] + 22)

            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.5, (200, 200, 200), font_thicknewss)
    cv2.imshow(filename, image)        
    cv2.waitKey(0)
    cv2.destroyWindow()
    