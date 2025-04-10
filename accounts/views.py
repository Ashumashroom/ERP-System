from datetime import datetime, timedelta, timezone
import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from home.utils import send_attendance_email, send_email_to_client, send_email_to_client_resetlink,send_login_email, send_otp_email, send_singnup_email
from .models import School, Student
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
import re
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import SetPasswordForm  # Assume you have a form to handle the new password
from django.utils.encoding import force_str

# School Registration
def register_school(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        school_name = request.POST.get('institution_name')
        school_code = request.POST.get('institution_code')

        # Check if the username, school name, or code already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('register_school')

        if School.objects.filter(name=school_name).exists():
            messages.error(request, "School name already exists. Please choose a different name.")
            return redirect('register_school')

        if School.objects.filter(code=school_code).exists():
            messages.error(request, "School code already exists. Please choose a different code.")
            return redirect('register_school')

        # Create a new user for the school
        user = User.objects.create_user(username=username, password=password, email=email)
        send_singnup_email(user)
        # Create a new school linked to the user
        School.objects.create(user=user, name=school_name, code=school_code)

        messages.success(request, "School registered successfully!")
        return redirect('register_school')

    return render(request, 'home/singn_up_admin.html')

# Student Registration
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import Student, School
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def register_student(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')
        school_code = request.POST.get('school_code')
        student_image = request.FILES.get('student_image')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_student')

        # Check if the student ID already exists
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists.")
            return redirect('register_student')

        # Attempt to get the school
        try:
            school = School.objects.get(code=school_code)
        except School.DoesNotExist:
            messages.error(request, "School not found.")
            return redirect('register_student')

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)
        send_singnup_email(user)

        # Rename the student image file to student_id
        if student_image:
            student_image.name = f"{student_id}{os.path.splitext(student_image.name)[1]}"  # Keep original extension
            file_path = default_storage.save(os.path.join("student/images", student_image.name), ContentFile(student_image.read()))

        # Create the student
        Student.objects.create(
            user=user,
            student_id=student_id,
            email=email,
            student_image=file_path,  # Save the path to the file here
            school=school
        )

        messages.success(request, "Student registered successfully!")
        return redirect('student_login')

    return render(request, 'home/sign_up.html')



# School Login
# def school_login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)
#         if user:
#             school = School.objects.filter(user=user).first()
#             if school:
#                 login(request, user)
#                 return redirect('home/home.html')  # Redirect to the school dashboard
#             else:
#                 messages.error(request, "School not found.")
#         else:
#             messages.error(request, "Invalid username or password.")

#     return render(request, 'home/login_admin.html')
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return redirect('school_login')

        if user is None:
            # Check if the username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Incorrect password.')
            else:
                messages.error(request, 'Invalid username.')
            return redirect('school_login')
        else:
            # This is to store data for session in the browser
           
            login(request, user)
            send_login_email(user)
            return redirect('home')

    return render(request, 'home/login_admin.html')

# Update Student Profile
def update_student(request):
    student = Student.objects.get(user=request.user)  # Get the logged-in student's profile
    if request.method == "POST":
        student.email = request.POST.get('email')
        if request.FILES.get('student_image'):
            student.student_image = request.FILES['student_image']  # Update the image if a new one is uploaded
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('student_dashboard')  # Redirect to some dashboard

    return render(request, 'update_student.html', {'student': student})

# Student Login
def student_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            student = Student.objects.filter(user=user).first()
            if student:
                login(request, user)
                send_login_email(user)
                return redirect('student_dashboard')  # Redirect to the student dashboard
            else:
                messages.error(request, "Student not found.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'home/login.html')

# Logout
def logout_view(request):
    logout(request) 
   
    return redirect('home')


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            user = User.objects.get(email=email)
            # Send reset email logic here
            send_email_to_client_resetlink(user) 
            messages.success(request, "A link to reset your password has been sent to your email.")
            return redirect("password_reset_done")
        except User.DoesNotExist:
            messages.error(request, "No user with this email address exists.")
            return redirect("password_reset_request")
    
    return render(request, "home/forgetpassword.html")
# def password_reset_request_otp(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
        
#         try:
#             user = User.objects.get(email=email)
#             # Send OTP email logic here
#             send_otp_email(user)  # Implement this function to send the OTP
            
            
#             return redirect('reset_password_otp', user_id=user.id)  # Redirect with user ID
#         except User.DoesNotExist:
#             messages.error(request, "No user with this email address exists.")
#             return redirect("password_reset_request")
    
#     return render(request, "home/otp_forget.html")

def password_reset_done(request):
    
    
    return render(request , "home/reset_done.html")

def send_email(request):
    send_email_to_client()
    return redirect('/')



def reset_password(request, uidb64, token):
    # Decode the user ID
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Check the token
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validate the password
            if new_password and confirm_password:
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match. Please try again.')
                elif len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters long.')
                elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                    messages.error(request, 'Password must contain at least one special character.')
                else:
                    user.set_password(new_password)  # Set the new password
                    user.save()  # Save the user instance
                    messages.success(request, 'Your password has been set. You can now log in.')
                    return redirect('school_login')  # Redirect to the login page or wherever you prefer
            else:
                messages.error(request, 'Please fill out both fields.')

        return render(request, 'home/reset_password.html', {
            'valid_link': True,
        })
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return render(request, 'home/reset_password.html', {
            'valid_link': False,
        })



def is_valid_email(email):
    # Basic email validation regex
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
def send_otp_email(user, otp):
    subject = "Your OTP for Password Reset"
    
    # Render the HTML template
    html_message = render_to_string('home/otp_templates.html', {'user': user, 'otp': otp})
    plain_message = strip_tags(html_message)  # Create a plain text version for email clients that don't support HTML
    
    # Send the email
    send_mail(
        subject,
        plain_message,
        'from@example.com',  # Replace with your sender email
        [user.email],
        html_message=html_message,  # Include HTML message
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta, datetime
import re

def password_reset_request_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not is_valid_email(email):
            messages.error(request, "Please enter a valid email address.")
            return redirect("password_reset_request")

        try:
            user = User.objects.get(email=email)
            otp = get_random_string(length=6, allowed_chars='0123456789')
            send_otp_email(user, otp)

            # Store OTP in the session with an expiration time as a string
            request.session['otp'] = otp
            request.session['otp_expiration'] = (timezone.now() + timedelta(minutes=5)).isoformat()

            messages.success(request, "An OTP has been sent to your email.")
            return redirect('reset_password_otp', user_id=user.id)

        except User.DoesNotExist:
            messages.error(request, "If this email address exists, an OTP has been sent.")
            return redirect("password_reset_request")

    return render(request, "home/otp_forget.html")

def reset_password_otp(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        session_otp = request.session.get('otp')
        otp_expiration_str = request.session.get('otp_expiration')

        # Convert expiration string back to datetime
        if otp_expiration_str:
            otp_expiration = datetime.fromisoformat(otp_expiration_str)
        else:
            otp_expiration = None

        # Check OTP and expiration
        if session_otp and session_otp == otp_input and (otp_expiration and timezone.now() < otp_expiration):
            if new_password and confirm_password:
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match. Please try again.')
                elif len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters long.')
                elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                    messages.error(request, 'Password must contain at least one special character.')
                else:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been reset. You can now log in.')
                    del request.session['otp']
                    del request.session['otp_expiration']
                    return redirect('school_login')
            else:
                messages.error(request, 'Please fill out both fields.')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')

    return render(request, 'home/reset_password_otp.html', {'user': user})


def resend_otp(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    otp = get_random_string(length=6, allowed_chars='0123456789')
    send_otp_email(user, otp)

    # Update OTP in the session with a new expiration
    request.session['otp'] = otp
    request.session['otp_expiration'] = timezone.now() + timedelta(minutes=5)

    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('reset_password_otp', user_id=user_id)
# views.py
# 
# new chap
# 
# 
# 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Attendance, Student
from django.utils import timezone

@login_required
# from django.shortcuts import render, redirect

@login_required
def student_dashboard(request):
    try:
        # Retrieve the student record for the logged-in user
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # Redirect to profile page if no student record is found
        return redirect('student_profile')
    
    # Get attendance records for the current student, ordered by date (most recent first)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    # Calculate total present count
    total_present_count = attendance_records.filter(status="Present").count()

    # Calculate attendance percentage
    total_records = attendance_records.count()
    attendance_percentage = (total_present_count / total_records * 100) if total_records > 0 else 0

    # Pass necessary data to the template
    return render(request, 'home/school_dashboard.html', {
        'student': student,
        'attendance_records': attendance_records,
        'total_present_count': total_present_count,
        'attendance_percentage': attendance_percentage,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .models import School, Student
from django.contrib.auth.decorators import login_required

@login_required

def school_dashboard(request):
    # Get the logged-in user's associated school
    school = get_object_or_404(School, id=request.user.school.id)

    # Fetch all students belonging to this school
    students = Student.objects.filter(school=school)

    # Handle the Add Student operation
    if request.method == "POST" and 'add_student' in request.POST:
        roll_number = request.POST.get('roll_number')
        username = request.POST.get('username')
        email = request.POST.get('email')
        student_image = request.FILES.get('student_image')
        password = request.POST['password']

        # Check if the username, email or student ID already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
        elif Student.objects.filter(student_id=roll_number).exists():
            messages.error(request, "Student ID already exists!")
        else:
            # Create a new student if no conflicts
            user = User.objects.create_user(username=username, email=email,password=password)
            student = Student.objects.create(
                school=school,
                user=user,
                student_id=roll_number,
                email=email,
                student_image=student_image
            )
            messages.success(request, "Student added successfully!")
            return redirect('school_dashboard')  # Redirect to refresh the page

    # Handle the Remove Student operation
    elif request.method == "POST" and 'remove_student' in request.POST:
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id, school=school)
        student.delete()
        messages.success(request, "Student removed successfully!")
        return redirect('school_dashboard')  # Redirect to refresh the page

    # Handle the Update Student operation
    elif request.method == "POST" and 'update_student' in request.POST:
        student_id = request.POST.get('student_id')  # Get the student ID from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        student_image = request.FILES.get('student_image')

        # Retrieve the student object using the student_id and school
        student = get_object_or_404(Student, id=student_id, school=school)
        
        # Update user information (username, email, password)
        user = student.user
        user.username = username
        user.email = email
        
        if password:
            user.set_password(password)  # Hash the new password if provided
        user.save()

        # Update student information (student_id is not updated)
        # If you want to allow updating student_id (roll_number), remove this check
        # but typically this should not change
        student.email = email  # Update student email
        if student_image:
            student.student_image = student_image  # Update the student image if provided
        student.save()

        messages.success(request, "Student updated successfully!")
        return redirect('school_dashboard')  # Redirect to refresh the page

    return render(request, 'home/student_dashboard.html', {'school': school, 'students': students})


# def student_dashboard(request, student_id):
#     student = Student.objects.get(student_id=student_id)
    
#     # Fetch attendance records for the student
#     attendance_records = Attendance.objects.filter(student=student)
    
#     # Prepare the context to pass to the template
#     context = {
#         'student': student,
#         'attendance_records': attendance_records,
#     }
    
#     return render(request, 'home/school_dashboard.html', context)
# views.py
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import Attendance, Student


@login_required
def mark_attendance(request):
    try:
        # Get the student record associated with the logged-in user
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_profile')  # Redirect if no student record is found

    # Get today's date
    today = timezone.now().date()
    
    # Adjust to Indian Standard Time (UTC+5:30)
    timi = timezone.now()
    timi_in_ist = timi + timedelta(hours=5, minutes=30)

    # Check if attendance is already recorded for today
    attendance, created = Attendance.objects.get_or_create(student=student, date=today)

    if request.method == 'POST':
        # Get the status from the submitted form
        status = request.POST.get('status')  # Either 'Present' or 'Absent'
        
        if status in ['Present', 'Absent']:  # Validate the status
            attendance.status = status
            attendance.time = timi_in_ist.time()  # Save only the time part
            attendance.save()  # Save the updated attendance record
            
            # Example of sending a signup email (implement your function accordingly)
            send_attendance_email(student)

            messages.success(request, "Attendance has been marked successfully.")
            return redirect('student_dashboard')  # Redirect after saving
        else:
            messages.error(request, "Invalid status. Please select 'Present' or 'Absent'.")

    # Render the attendance page with current attendance data
    return render(request, 'home/mark_attendance.html', {
        'attendance': attendance,
        'student': student,
    })

# 
# 
# 
# myapp/views.py
from django.http import HttpResponse
import subprocess
import os

# myapp/views.py
from django.http import HttpResponse
import subprocess
import os

def run_main_script(request):
    try:
        # Go up one directory level from the current file's location (myapp/views.py)
        project_root = os.path.dirname(os.path.dirname(__file__))  # Now we're at 'myproject'
        
        # Join the project root path with 'main.py' to get the script's full path
        script_path = os.path.join(project_root, 'main.py')
        
        # Run the script using subprocess
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        
        # Check for success or failure in running the script
        if result.returncode == 0:
            return HttpResponse(f"Script output:\n{result.stdout}")
        else:
            return HttpResponse(f"Script error:\n{result.stderr}", status=500)
            
    except Exception as e:
        return HttpResponse(f"Failed to run script: {str(e)}", status=500)
def sac(request):
    # Example context data
    
    
    return render(request, 'home/sacstu.html')
