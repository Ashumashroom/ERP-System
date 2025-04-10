import os
import django
import pickle
import cv2
import cvzone
import face_recognition
import numpy as np
from django.utils import timezone
from home.utils import send_attendance_email

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "first.settings")
django.setup()

from accounts.models import Student, Attendance

# Load the encodings file
try:
    with open('encodefile.p', 'rb') as file:
        encodeListKnownwithids = pickle.load(file)
        encodeListKnown, studentIds = encodeListKnownwithids
except (FileNotFoundError, EOFError, pickle.PickleError) as e:
    print(f"Error: Could not load face encodings file - {e}")
    exit()

# Set up the video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Preprocess the background and mode images
imgBackground = cv2.resize(cv2.imread('Resources/Designer2.jpeg'), (1700, 1300))
folderModePath = 'Resources/Modes'
imgModeList = [
    cv2.resize(cv2.imread(os.path.join(folderModePath, path)), (632, 1160))
    for path in os.listdir(folderModePath)
    if path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
]

if len(imgModeList) < 4:
    print("Error: Ensure you have at least four images in the Modes folder.")
    exit()

# Attendance configuration
attendance_width, attendance_height = 1280, 960
tolerance = 0.4
frame_skip = 5  # Process every 5th frame
frame_counter = 0

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    frame_counter += 1
    if frame_counter % frame_skip != 0:
        continue

    img_resized = cv2.resize(img, (attendance_width, attendance_height))
    imgBackground[132:132 + attendance_height, 40:40 + attendance_width] = img_resized
    imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[2]  # Display "processing"

    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Optimize for processing
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgs, model="hog")  # Switch to 'hog'
    encodeCurrFrame = face_recognition.face_encodings(imgs, faceCurrFrame)

    for encodeFace, faceloc in zip(encodeCurrFrame, faceCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=tolerance)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            studentId = studentIds[matchIndex]
            x1, y1, x2, y2 = faceloc[3] * 4, faceloc[0] * 4, faceloc[1] * 4, faceloc[2] * 4
            bbox = (55 + x1, 162 + y1, int(0.7 * (x2 - x1)), int(0.7 * (y2 - y1)))
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            try:
                student = Student.objects.get(student_id=studentId)
                imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[3]
                cv2.putText(imgBackground, student.user.username, (x1 + 60, y2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=timezone.now().date(),
        
                    defaults={'status': 'Present'}
                )

                if not created:
                    imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[1]  # "Already marked"
                else:
                    imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[0]  # "Marked"
                    send_attendance_email(student)
                    attendance.time = timezone.now()
                    print(f"Attendance marked for: {student.user.username}")

            except Student.DoesNotExist:
                print(f"No student found with ID {studentId}")

    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# import os
# import django
# import pickle
# import cv2
# import cvzone
# import face_recognition
# import numpy as np
# from django.utils import timezone
# from home.utils import send_attendance_email

# # Set up Django settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "first.settings")
# django.setup()

# from accounts.models import Student, Attendance

# # Load the encodings file
# try:
#     with open('encodefile.p', 'rb') as file:
#         encodeListKnownwithids = pickle.load(file)
#         encodeListKnown, studentIds = encodeListKnownwithids
# except (FileNotFoundError, EOFError, pickle.PickleError) as e:
#     print(f"Error: Could not load face encodings file - {e}")
#     exit()

# # Set up the video capture
# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Error: Could not open camera.")
#     exit()

# # Load and resize the background image
# imgBackground = cv2.imread('Resources/Designer2.jpeg')
# if imgBackground is None:
#     print("Error: Could not read the background image. Check the file path.")
#     exit()
# imgBackground = cv2.resize(imgBackground, (1700, 1300))

# # Load mode images
# folderModePath = 'Resources/Modes'
# imgModeList = []
# for path in os.listdir(folderModePath):
#     if path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
#         mode_img = cv2.imread(os.path.join(folderModePath, path))
#         if mode_img is not None:
#             mode_img_resized = cv2.resize(mode_img, (632, 1160))
#             imgModeList.append(mode_img_resized)

# # Verify images loaded
# if len(imgModeList) < 4:
#     print("Error: Ensure you have at least four images in the Modes folder.")
#     exit()

# # Set attendance image dimensions
# attendance_width, attendance_height = 1280, 960  # Increased resolution
# tolerance = 0.35  # Stricter tolerance for accuracy

# # Switch to CNN model for face detection
# face_detection_model = "cnn"

# while True:
#     success, img = cap.read()
#     if not success:
#         print("Failed to capture image")
#         break

#     # Resize the captured image for better processing
#     img_resized = cv2.resize(img, (attendance_width, attendance_height))
#     imgBackground[132:132 + attendance_height, 40:40 + attendance_width] = img_resized
#     imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[2]  # Display "processing" initially

#     # Resize and convert for face recognition processing
#     imgs = cv2.resize(img, (0, 0), None, 0.5, 0.5)  # Increase processing size for better results
#     imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

#     # Detect and encode faces
#     faceCurrFrame = face_recognition.face_locations(imgs, model=face_detection_model)
#     encodeCurrFrame = face_recognition.face_encodings(imgs, faceCurrFrame)

#     # Place the captured image on the background
#     imgBackground[132:132 + attendance_height, 40:40 + attendance_width] = img_resized

#     for encodeFace, faceloc in zip(encodeCurrFrame, faceCurrFrame):
#         matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=tolerance)
#         faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
#         matchIndex = np.argmin(faceDis)

#         # Debugging output for face matching
#         print(f"Face distances: {faceDis}")
#         print(f"Matches: {matches}")
#         print(f"Selected match index: {matchIndex}")

#         if matches[matchIndex]:
#             studentId = studentIds[matchIndex]
#             x1, y1, x2, y2 = faceloc[3] * 2, faceloc[0] * 2, faceloc[1] * 2, faceloc[2] * 2
#             bbox = (55 + x1, 162 + y1, int(0.7 * (x2 - x1)), int(0.7 * (y2 - y1)))
#             imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

#             try:
#                 # Retrieve the student and display "student info"
#                 student = Student.objects.get(student_id=studentId)
#                 imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[3]
#                 cv2.putText(imgBackground, student.user.username, (x1 + 60, y2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

#                 # Check attendance status
#                 attendance, created = Attendance.objects.get_or_create(
#                     student=student,
#                     date=timezone.now().date(),
                    
#                     defaults={'status': 'Present'}
#                 )

#                 if not created:
#                     # Attendance already marked - show "already marked"
#                     imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[1]
#                 else:
#                     # Attendance marked for the first time - show "marked"
#                     imgBackground[70:70 + 1160, 1033:1033 + 632] = imgModeList[0]
#                     send_attendance_email(student)
#                     attendance.time = timezone.now()
#                     print(f"Attendance marked for: {student.user.username}")

#             except Student.DoesNotExist:
#                 print(f"No student found with ID {studentId}")

#     # Show the final image
#     cv2.imshow("Face Attendance", imgBackground)

#     # Exit on 'q' key
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release and close
# cap.release()
# cv2.destroyAllWindows()
