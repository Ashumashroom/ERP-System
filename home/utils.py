
from datetime import timedelta
import random
from urllib import request
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.html import strip_tags


def send_email_to_client():
    subject = "Open source "
    message = "Your one time password (otp) is 3647 for reset your password."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ["ashsihranjan6288@gmail.com"]
    
    send_mail(subject, message, from_email, recipient_list)


def send_email_to_client_resetlink(user):
    subject = "Password Reset Requested"
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

    # Render the email template
    html_message = render_to_string('home/password_reset_email.html', {
        'user': user,
        'reset_link': reset_link,
    })
    
    plain_message = strip_tags(html_message)  # Optionally create a plain text version

    # Send the email
    send_mail(
        subject,
        plain_message,  # This is for the plain text version
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        html_message=html_message  # This is the HTML version
    )
    # 
    # 
    # 
def send_login_email(user):
     subject = "Login Notification"
     message = f"""
     Hello {user.username},

     You have successfully logged into the Open_Source website.

     Regards,
     The Open_Source Team
     """

    # Send the email
     send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in your settings.py
        [user.email],
        fail_silently=False,
    )
def send_singnup_email(user):
     subject = "SingUp Notification"
     message = f"""
     Hello {user.username},

     You have successfully resistered your account from  website.

     Regards,
     The Open_Source Team
     """

    # Send the email
     send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in your settings.py
        [user.email],
        fail_silently=False,
    )
     
def send_otp_email(user):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    # Store the OTP in the session for verification later
    # (Make sure to import the request in the view where you call this function)
    request.session['otp'] = otp
    
    subject = 'Your OTP for Password Reset'
    message = f'Your OTP is {otp}. Use this to reset your password.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

   
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

def send_attendance_email(student):
    current_time = timezone.now()  # Format as needed
    timi_in_ist = current_time + timedelta(hours=5, minutes=30)
    
    formatted_time = timi_in_ist.strftime('%Y-%m-%d %H:%M:%S')
    subject = "Attendence Notification"
    message = f"""
    Hello {student.user.username},

    Your ward has entered the school on {formatted_time}.

    Regards,
    The Open Source Team
    """

    # Send the email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in your settings.py
        [student.user.email],
        fail_silently=False,
    )

