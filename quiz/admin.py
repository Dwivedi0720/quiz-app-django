from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, StudentAnswer

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'difficulty', 'is_active', 'pass_percentage', 'created_at']
    list_filter = ['difficulty', 'is_active', 'created_by']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'correct_answer', 'marks', 'time_limit', 'order']
    list_filter = ['quiz']
    search_fields = ['question_text']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'status', 'score', 'percentage', 'start_time', 'end_time']
    list_filter = ['status', 'quiz']
    search_fields = ['student__username', 'quiz__title']

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_answer', 'is_correct']
    list_filter = ['is_correct']
