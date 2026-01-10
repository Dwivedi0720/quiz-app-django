from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from quiz.models import QuizAttempt
from django.utils import timezone

class DailyProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_progress')
    date = models.DateField()
    quizzes_attempted = models.IntegerField(default=0)
    quizzes_passed = models.IntegerField(default=0)
    quizzes_failed = models.IntegerField(default=0)
    total_score = models.FloatField(default=0)
    total_marks = models.FloatField(default=0)
    average_percentage = models.FloatField(default=0)
    time_spent = models.IntegerField(default=0, help_text='Time spent in seconds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.date}"

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Daily Progress'


class OverallProgress(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='overall_progress')
    total_quizzes_attempted = models.IntegerField(default=0)
    total_quizzes_passed = models.IntegerField(default=0)
    total_quizzes_failed = models.IntegerField(default=0)
    total_score = models.FloatField(default=0)
    total_marks = models.FloatField(default=0)
    overall_percentage = models.FloatField(default=0)
    total_time_spent = models.IntegerField(default=0, help_text='Total time spent in seconds')
    highest_score = models.FloatField(default=0)
    lowest_score = models.FloatField(default=0)
    last_quiz_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - Overall Progress"

    class Meta:
        verbose_name_plural = 'Overall Progress'


@receiver(post_save, sender=QuizAttempt)
def update_progress(sender, instance, created, **kwargs):
    """Update daily and overall progress when quiz attempt is completed"""
    if instance.status == 'completed':
        student = instance.student
        today = timezone.now().date()
        
        # Update daily progress
        daily_progress, created = DailyProgress.objects.get_or_create(
            student=student,
            date=today,
            defaults={
                'quizzes_attempted': 0,
                'quizzes_passed': 0,
                'quizzes_failed': 0,
                'total_score': 0,
                'total_marks': 0,
                'time_spent': 0,
            }
        )
        
        # Recalculate daily stats
        today_attempts = QuizAttempt.objects.filter(
            student=student,
            status='completed',
            start_time__date=today
        )
        
        daily_progress.quizzes_attempted = today_attempts.count()
        daily_progress.quizzes_passed = today_attempts.filter(percentage__gte=models.F('quiz__pass_percentage')).count()
        daily_progress.quizzes_failed = daily_progress.quizzes_attempted - daily_progress.quizzes_passed
        daily_progress.total_score = today_attempts.aggregate(models.Sum('score'))['score__sum'] or 0
        daily_progress.total_marks = today_attempts.aggregate(models.Sum('total_marks'))['total_marks__sum'] or 0
        daily_progress.average_percentage = (daily_progress.total_score / daily_progress.total_marks * 100) if daily_progress.total_marks > 0 else 0
        daily_progress.time_spent = today_attempts.aggregate(models.Sum('time_taken'))['time_taken__sum'] or 0
        daily_progress.save()
        
        # Update overall progress
        overall_progress, created = OverallProgress.objects.get_or_create(student=student)
        
        all_attempts = QuizAttempt.objects.filter(student=student, status='completed')
        
        overall_progress.total_quizzes_attempted = all_attempts.count()
        overall_progress.total_quizzes_passed = all_attempts.filter(percentage__gte=models.F('quiz__pass_percentage')).count()
        overall_progress.total_quizzes_failed = overall_progress.total_quizzes_attempted - overall_progress.total_quizzes_passed
        overall_progress.total_score = all_attempts.aggregate(models.Sum('score'))['score__sum'] or 0
        overall_progress.total_marks = all_attempts.aggregate(models.Sum('total_marks'))['total_marks__sum'] or 0
        overall_progress.overall_percentage = (overall_progress.total_score / overall_progress.total_marks * 100) if overall_progress.total_marks > 0 else 0
        overall_progress.total_time_spent = all_attempts.aggregate(models.Sum('time_taken'))['time_taken__sum'] or 0
        overall_progress.highest_score = all_attempts.aggregate(models.Max('percentage'))['percentage__max'] or 0
        overall_progress.lowest_score = all_attempts.aggregate(models.Min('percentage'))['percentage__min'] or 0
        overall_progress.last_quiz_date = instance.end_time
        overall_progress.save()