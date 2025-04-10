"""first URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from home.views import *
from accounts.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
     path('python_project/' ,Home ,name='app1fun'),
     path('admin/', admin.site.urls),
     path('', home ,name="home"),
     path('student_login/',student_login,name="student_login"),
     path('admin_register/',register_school,name="register_school"),
     path('student_register/',register_student,name="register_student"),
     path('logout_view/',logout_view,name="logout_view"),
     path('student_dashboard/',student_dashboard,name="student_dashboard"),
     path('school_login/',login_page,name="school_login"),
     path('password_reset_request/',password_reset_request,name="password_reset_request"),
     path('password_reset_request_otp/',password_reset_request_otp,name="password_reset_request_otp"),
    #  path('reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('reset-password/<uidb64>/<token>/', reset_password, name="reset_password"),
     path('password_reset_done/',password_reset_done,name="password_reset_done"),
     path('send_email',send_email,name="send_email"),
    
    path('reset-password-otp/<int:user_id>/', reset_password_otp, name="reset_password_otp"),
    path('resend-otp/<int:user_id>/', resend_otp, name="resend_otp"),
     path('mark-attendance/', mark_attendance, name='mark_attendance'),
    path('run-script/', run_main_script, name='run_script'),
     path('school_dashboard/',school_dashboard,name="school_dashboard"),
       path('school/post_announcement/', post_announcement, name='post_announcement'),
       path('chat/', chat_list, name='chat_list'),
    # path('chat/<int:student_id>/', chat_detail, name='chat_detail')
  


    path("", chat_home, name="chat_home"),  # Main chat page
    path("chat/<int:student_id>/", chat_detail, name="chat_detail"),  # Chat with a specific student
     path('chat/student/<int:school_id>/', student_chat_detail, name='student_chat_detail'),
      path('task',dashboard23 , name='dashboard23'),
         path('task_list',todo_list_items , name='todo_list_items'),
  path('sac',sac , name='sac')
# ]¸
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root = settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()        


