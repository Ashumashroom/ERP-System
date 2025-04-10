import threading
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import *
from .models import UserList
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import School, Announcement, Student
from django.utils.timezone import now
from django.urls import reverse

def home(request):
    if request.user.is_authenticated:
        try:
            # Try to fetch the school if the user is associated with a School object directly
            if hasattr(request.user, 'school'):
                # This is for users with a direct relation to School (e.g., school admins)
                user_school = request.user.school
            else:
                # This is for students, where the user is associated with a student object
                student = Student.objects.get(user=request.user)  # Find the student related to the user
                user_school = student.school  # Fetch the school via the student model

            # Now, fetch the announcements for the user's school
            announcements = Announcement.objects.filter(school=user_school)

        except (School.DoesNotExist, Student.DoesNotExist):
            # If no school is found for the user (i.e., no Student and no associated School)
            announcements = []
            return HttpResponse("Your account is not associated with a school.")

    else:
        announcements = []

    return render(request, 'home/home.html', {
        'announcements': announcements,
    })



import cv2
import os
import threading
import numpy as np
from skimage.metrics import structural_similarity as ssim
from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2
import os
import threading
from django.http import StreamingHttpResponse
from django.shortcuts import render
from skimage.metrics import structural_similarity as ssim

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Path to the folder containing user images
IMAGE_BASE_FOLDER = os.path.join('media')

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame.copy()  # Make a copy of the frame to avoid modifying the original
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            matched_file_name = self.check_attendance(face_img)
            if matched_file_name:
                # If matched, display username/file name
                cv2.putText(image, f"Matched: {matched_file_name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                color = (0, 255, 0)  # Green for recognized faces
            else:
                cv2.putText(image, "No Match", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                color = (0, 0, 255)  # Red for unknown faces
            
            # Draw a rectangle around the face
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def check_attendance(self, face_img):
        """Check if the face matches any user's images."""
        for user_folder in os.listdir(IMAGE_BASE_FOLDER):
            user_folder_path = os.path.join(IMAGE_BASE_FOLDER, user_folder)
            if os.path.isdir(user_folder_path):
                for image_file in os.listdir(user_folder_path):
                    if image_file.endswith('.jpg') or image_file.endswith('.png'):
                        known_face_path = os.path.join(user_folder_path, image_file)
                        known_face = cv2.imread(known_face_path, cv2.IMREAD_GRAYSCALE)
                        known_face = cv2.resize(known_face, (face_img.shape[1], face_img.shape[0]))

                        # Compare the faces using SSIM
                        score, _ = ssim(face_img, known_face, full=True)
                        if 0.3 <= score <= 0.9:
                            return user_folder  # Return the username or folder name of the matched user
        return None

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def Home(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error: {e}")
    return render(request, 'home/app1.html')
# code for message
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from datetime import datetime

# View to show all announcements for a school
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.utils import timezone

# View to post a notice (for school admins)
@login_required
def post_announcement(request):

    school = get_object_or_404(School, id=request.user.school.id)
    
    if request.user == school.user:  # Check if the logged-in user is the school admin
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            announcement = Announcement.objects.create(
                school=school,
                title=title,
                content=content,
               
                
            )
            return redirect('home')  # Just redirect to home, announcements will be passed in the context

    
    return render(request, 'home/post_ann.html', {'school': school})

# View to display announcements for students
@login_required
def view_announcements(request, school_id):
    school = School.objects.get(id=school_id)
    announcements = Announcement.objects.filter(school=school).order_by('-date_posted')

    # Mark unread notices as read when they are opened
    if request.user.is_authenticated:
        Announcement.objects.filter(is_read=False).update(is_read=True)

    return render(request, 'messaging/announcements.html', {'school': school, 'announcements': announcements})

# View to show all messages between a school and a student
# @login_required
# def view_messages(request, student_id):
#     student = User.objects.get(id=student_id)
#     messages_received = Message.objects.filter(receiver=student).order_by('-timestamp')
#     messages_sent = Message.objects.filter(sender=request.user).order_by('-timestamp')
    
#     return render(request, 'messaging/messages.html', {
#         'messages_received': messages_received,
#         'messages_sent': messages_sent,
#         'student': student
#     })

# # View to send a message to a student
# @login_required
# def send_message(request, student_id):
#     student = User.objects.get(id=student_id)
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         message = Message(sender=request.user, receiver=student, content=content)
#         message.save()
#         return redirect('view_messages', student_id=student.id)
#     return render(request, 'messaging/send_message.html', {'student': student})
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


# Chatbox for the school to display all students
@login_required
def chat_list(request):
    school = get_object_or_404(School, user=request.user)
    students = Student.objects.filter(school=school)
    return render(request, 'home/chat_list.html', {'students': students})

# Chat messages between school and a specific student
@login_required
def chat_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id, school__user=request.user)
    messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=student.user)) |
        (models.Q(sender=student.user) & models.Q(receiver=request.user))
    ).order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=student.user,
                content=content
            )
    
    return render(request, 'home/chat_datail.html', {'student': student, 'messages': messages})
# def chat_view(request, student_id):
#     current_student = Student.objects.get(user=request.user)
#     recipient = Student.objects.get(id=student_id)
    
#     if request.method == 'POST':
#         # Handle message sending
#         content = request.POST.get('message')
#         if content:
#             new_message = Message(sender=current_student, receiver=recipient, content=content)
#             new_message.save()
#             return redirect('chat_view', student_id=student_id)  # Redirect to the same page after sending a message
    
#     # Fetch all messages between the current student and the selected recipient
#     messages = Message.objects.filter(
#         (models.Q(sender=current_student) & models.Q(receiver=recipient)) |
#         (models.Q(sender=recipient) & models.Q(receiver=current_student))
#     ).order_by('timestamp')
    
#     return render(request, 'chatbox.html', {
#         'student': current_student,
#         'recipient': recipient,
#         'messages': messages,
#         'students': Student.objects.all(),  # Include the list of students for the sidebar
#     })
def chat_home(request):
    """Display a list of students."""
    students = Student.objects.all()  # Adjust filtering as needed
    return render(request, "home/chat_list.html", {"students": students, "messages": []})

@login_required
def chat_detail(request, student_id):
    """Display chat with a specific student."""
    student = get_object_or_404(Student, id=student_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=student.user
    ) | Message.objects.filter(
        sender=student.user, receiver=request.user
    ).order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=student.user,
                content=content,
                timestamp=now(),
            )
        return redirect("chat_detail", student_id=student_id)

    return render(
        request,
        "home/chat_list.html",
        {"students": Student.objects.all(), "messages": messages, "student": student},
    )

def student_chat_detail(request, school_id):
    """Display chat between student and their school (student to school chat)."""
    student = get_object_or_404(Student, user=request.user)  # Get current student
    school = get_object_or_404(School, id=school_id)  # Get the selected school

    # Ensure the student is chatting with their own school
    if student.school != school:
        return redirect("chat_home")  # Redirect to chat home if the school is incorrect

    # Fetch all messages between this student and the school
    messages = Message.objects.filter(
        sender=request.user, receiver=school.user
    ) | Message.objects.filter(
        sender=school.user, receiver=request.user
    ).order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            Message.objects.create(
                sender=request.user,  # Student is the sender
                receiver=school.user,  # School's user is the receiver
                content=content,
                timestamp=now(),
            )
        return redirect("student_chat_detail", school_id=school_id)

    return render(
        request,
        "home/student_chat_detail.html",  # New template for student chat
        {"messages": messages, "student": student, "school": school},
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# 
# 
# 
# 
# 
# 
# 
# 


@login_required
def dashboard23(request):
    # Get all To-Do lists for the logged-in student
    student = request.user.student
    todo_lists = ToDoList.objects.filter(student=student)

    if request.method == "POST":
        # Add a new To-Do List
        if 'add_todo_list' in request.POST:
            title = request.POST.get('title')
            todo_list = ToDoList(student=student, title=title)
            todo_list.save()
            return redirect('dashboard23')  # Refresh the page to show the new To-Do List

        # Delete a To-Do List
        if 'delete_todo_list' in request.POST:
            todo_list_id = request.POST.get('todo_list_id')
            todo_list = ToDoList.objects.get(id=todo_list_id)
            # todo_list.delete() 
            # hide for not delete the do list 
            return redirect('dashboard23')  # Refresh the page after deletion

    # Calculate progress for each To-Do List
    for todo_list in todo_lists:
        total_items = todo_list.items.count()
        if total_items > 0:
            completed_items = todo_list.items.filter(is_done=True).count()
            todo_list.progress = (completed_items / total_items) * 100
        else:
            todo_list.progress = 0

    return render(request, 'home/aa.html', {'todo_lists': todo_lists})
# 
# 
# 
## views.py


def todo_list_items(request):
    # Get the todo_list_id from query parameters
    todo_list_id = request.GET.get('todo_list_id')

    # Check if todo_list_id is provided
    if not todo_list_id:
        return HttpResponseBadRequest("Missing todo_list_id parameter.")

    # Retrieve the To-Do List associated with the logged-in student and specific id
    todo_list = get_object_or_404(ToDoList, id=todo_list_id, student=request.user.student)
    items = todo_list.items.all()

    if request.method == "POST":
        # Handle adding a new task
        if 'add_todo_item' in request.POST:
            description = request.POST.get('description')
            problem_link = request.POST.get('problem_link')
            ToDoItem.objects.create(todo_list=todo_list, description=description, problem_link=problem_link)
            return redirect(f'{reverse("todo_list_items")}?todo_list_id={todo_list_id}')

        # Handle actions on existing tasks
        item_id = request.POST.get('item_id')
        item = get_object_or_404(ToDoItem, id=item_id, todo_list=todo_list)

        # Handle deleting a task
        if 'delete_todo_item' in request.POST:
            item.delete()
            return redirect(f'{reverse("todo_list_items")}?todo_list_id={todo_list_id}')

        # Handle toggling task completion (done/undone)
        if 'toggle_done' in request.POST:
            item.is_done = not item.is_done
            item.save()
            return redirect(f'{reverse("todo_list_items")}?todo_list_id={todo_list_id}')

        # Handle saving the note
        if 'save_note' in request.POST:
            note = request.POST.get('note', '')
            item.note = note
            item.save()
            return redirect(f'{reverse("todo_list_items")}?todo_list_id={todo_list_id}')

        # Handle toggling the importance (star/unstar)
        if 'star_task' in request.POST:
            item.is_important = not item.is_important
            item.save()
            return redirect(f'{reverse("todo_list_items")}?todo_list_id={todo_list_id}')

    return render(request, 'home/todo_items.html', {'todo_list': todo_list, 'items': items})
