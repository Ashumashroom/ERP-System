from django.db import models
from django.contrib.auth.models import User
import os

class UserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_name = models.CharField(max_length=100)
    student_enrolment_no = models.TextField()  # Corrected initialization
    institution_id = models.CharField(max_length=100)
    student_image = models.ImageField(upload_to='student_data_base_images', null=True, blank=True)

    def save(self, *args, **kwargs):
        # If the image field has changed and there's an existing image, delete it
        if self.pk:  # If the object already exists
            old_image = UserList.objects.get(pk=self.pk).student_image
            if old_image and old_image != self.student_image:
                if os.path.isfile(old_image.path):
                    try:
                        os.remove(old_image.path)
                    except Exception as e:
                        # Handle the exception or log it if needed
                        print(f"Error deleting file: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.student_name

    class Meta:
        verbose_name = "User List"
        verbose_name_plural = "User Lists"
        ordering = ['student_name']  # Optional: order by student name
