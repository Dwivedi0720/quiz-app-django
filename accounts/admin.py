from django.contrib import admin
from .models import StudentProfile, TrainerProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_number', 'assigned_trainer', 'is_active', 'created_at']
    list_filter = ['is_active', 'assigned_trainer']
    search_fields = ['user__username', 'user__email', 'enrollment_number']


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'employee_id',
        'specialization',
        'is_active',
        'assigned_by_admin',
        'created_at',
    ]
    list_filter = ['is_active', 'assigned_by_admin']
    search_fields = ['user__username', 'user__email', 'employee_id']
