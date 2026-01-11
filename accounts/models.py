from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    enrollment_number = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    assigned_trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='assigned_students', limit_choices_to={'is_staff': True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.enrollment_number}"

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'


class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)

    # ADMIN CONTROL
    is_active = models.BooleanField(default=False)
    assigned_by_admin = models.BooleanField(default=False)

    # ADD THIS 👇
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Trainer"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile based on user role"""
    if created:
        if instance.is_staff and not instance.is_superuser:
            # Create trainer profile
            employee_id = f"TR{instance.id:05d}"
            TrainerProfile.objects.get_or_create(user=instance, defaults={'employee_id': employee_id})
        elif not instance.is_staff and not instance.is_superuser:
            # Create student profile
            enrollment_number = f"ST{instance.id:05d}"
            StudentProfile.objects.get_or_create(user=instance, defaults={'enrollment_number': enrollment_number})