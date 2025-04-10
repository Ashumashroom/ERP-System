from django.contrib import admin
from .models import School, Student

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'user')  # Columns to display in the admin list view
    search_fields = ('name', 'code')  # Searchable fields

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'school')  # Columns to display in the admin list view
    search_fields = ('student_id', 'email', 'user__username')  # Searchable fields
    list_filter = ('school',)  # Add filter by school

# Optionally, customize how the models are displayed and managed
