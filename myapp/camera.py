import cv2
import os
import pickle
import numpy as np
from .predict_face import predict
import warnings

warnings.filterwarnings("ignore")


face_mask = ["No mask", "Masked"]
# load model
# print(os.getcwd())
faceNet = cv2.dnn.readNet(
    os.path.join("model_ml/deploy.prototxt.txt"),
    os.path.join("model_ml/res10_300x300_ssd_iter_140000.caffemodel"),
)

with open("model_ml/outfile", "rb") as fp:
    myW = pickle.load(fp)


class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        # self.cap = self.cap.set(3, 1280)
        # self.cap = self.cap.set(4, 720)
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        faceNet.setInput(blob)
        detections = faceNet.forward()

        image_train = np.empty((0, 15552), int)  # 5184

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence < 0.5:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
            face = frame[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (54, 96))
            # face = rgb2gray(face) #for converse to GRAY picture
            image = np.array(face)
            image = image.reshape(1, -1)
            image_train = np.vstack((image_train, image)) / 255.0
            result = np.argmax(predict(image, myW))

            if result == 0:
                label = face_mask[result]
                color = (0, 0, 255)
            else:
                label = face_mask[result]
                color = (0, 255, 0)

            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            # cv2.rectangle(frame, (startX, startY - 40), (endX, startY), color, -1)
            # cv2.putText(frame, label, (startX + 10, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()
