from django.contrib import admin
from .models import DailyProgress, OverallProgress

@admin.register(DailyProgress)
class DailyProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'quizzes_attempted', 'quizzes_passed', 'average_percentage']
    list_filter = ['date', 'student']
    search_fields = ['student__username']

@admin.register(OverallProgress)
class OverallProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_quizzes_attempted', 'total_quizzes_passed', 'overall_percentage']
    search_fields = ['student__username']