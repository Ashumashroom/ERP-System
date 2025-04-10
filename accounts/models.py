from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time

# School model
class School(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

# Student model
class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    student_image = models.ImageField(upload_to="students/images")

    def __str__(self):
        return f"{self.user.username} ({self.student_id})"

# Attendance model with DateTimeField
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)  # This will store the local date and time
    time = models.TimeField(default=time(0, 0))
    
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Absent'
    )

    def __str__(self):
        return f"{self.student.student_id} - {self.date} - {self.status}"

# Announcement model for school-wide messages
class Announcement(models.Model):
    school = models.ForeignKey(School, related_name="announcements", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateTimeField(default=datetime.now)
    
    def __str__(self):
        return f"Announcement for {self.school.name} - {self.title}"

# Message model for private communication between school and student
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
class ToDoList(models.Model):
    student = models.ForeignKey(Student, related_name="todo_lists", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_on = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.title} (Student: {self.student.user.username})"

# ToDoItem model to manage tasks within a To-Do List
class ToDoItem(models.Model):
    todo_list = models.ForeignKey(ToDoList, related_name="items", on_delete=models.CASCADE)
    problem_link = models.URLField()
    description = models.CharField(max_length=255)
    note = models.TextField(blank=True)  # New field for adding notes
    is_done = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)  # New field to mark tasks as important
    added_on = models.DateTimeField(default=datetime.now)

    def __str__(self):
        status = "✅ Done" if self.is_done else "❌ Pending"
        importance = "⭐ Important" if self.is_important else "🔹 Not Important"
        return f"{self.description} - {status} - {importance}"