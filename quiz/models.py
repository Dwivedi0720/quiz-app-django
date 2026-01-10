from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    pass_percentage = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return self.questions.aggregate(models.Sum('marks'))['marks__sum'] or 0

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    marks = models.IntegerField(default=1)
    time_limit = models.IntegerField(default=60, help_text='Time limit in seconds')
    explanation = models.TextField(blank=True, help_text='Explanation for correct answer')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

    class Meta:
        ordering = ['order', 'created_at']


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.FloatField(default=0)
    total_marks = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(default=0, help_text='Time taken in seconds')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.status}"

    @property
    def is_passed(self):
        return self.percentage >= self.quiz.pass_percentage

    def calculate_score(self):
        correct_answers = self.answers.filter(is_correct=True).count()
        total_questions = self.quiz.questions.count()
        self.score = self.answers.filter(is_correct=True).aggregate(
            models.Sum('question__marks'))['question__marks__sum'] or 0
        self.total_marks = self.quiz.total_marks
        self.percentage = (self.score / self.total_marks * 100) if self.total_marks > 0 else 0
        self.save()

    class Meta:
        ordering = ['-start_time']
        unique_together = ['student', 'quiz']


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    is_correct = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0, help_text='Time taken in seconds')
    answered_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_correct = (self.selected_answer == self.question.correct_answer)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attempt.student.username} - Q{self.question.order}"

    class Meta:
        unique_together = ['attempt', 'question']