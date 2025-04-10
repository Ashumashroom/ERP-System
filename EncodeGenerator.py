import cv2
import face_recognition
import pickle

import os

folderPath = 'media/student/images'
PathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    # print(path)
    # print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])
print(studentIds)



def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList    


encodeListKnown = findEncodings(imgList)
encodeListKnownwithids = [encodeListKnown,studentIds]


file = open("encodefile.p" , 'wb')

pickle.dump(encodeListKnownwithids,file)