from django import forms
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm

class SetPasswordForm(BaseSetPasswordForm):
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
from django import forms
from .models import Attendance
