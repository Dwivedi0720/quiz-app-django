from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import StudentProfile
from quiz.models import Quiz, Question, QuizAttempt
from progress.models import DailyProgress, OverallProgress
from .forms import QuizForm, QuestionForm
from django.forms import formset_factory

def is_trainer(user):
    return user.is_staff and not user.is_superuser

@login_required
@user_passes_test(is_trainer)
def dashboard(request):
    trainer = request.user
    students = User.objects.filter(student_profile__assigned_trainer=trainer)
    quizzes = Quiz.objects.filter(created_by=trainer)
    
    # Statistics
    total_students = students.count()
    active_students = students.filter(student_profile__is_active=True).count()
    total_quizzes = quizzes.count()
    total_attempts = QuizAttempt.objects.filter(quiz__created_by=trainer).count()
    
    # Recent attempts
    recent_attempts = QuizAttempt.objects.filter(
        quiz__created_by=trainer,
        status='completed'
    ).select_related('student', 'quiz').order_by('-end_time')[:10]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'recent_attempts': recent_attempts
    }
    return render(request, 'trainer/dashboard.html', context)

@login_required
@user_passes_test(is_trainer)
def create_quiz(request):
    QuestionFormSet = formset_factory(QuestionForm, extra=5, max_num=20)
    
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')
        
        if quiz_form.is_valid() and question_formset.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            
            order = 1
            for form in question_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    question = form.save(commit=False)
                    question.quiz = quiz
                    question.order = order
                    question.save()
                    order += 1
            
            messages.success(request, f'Quiz "{quiz.title}" created successfully!')
            return redirect('trainer:manage_quizzes')
    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet(prefix='questions')
    
    context = {
        'quiz_form': quiz_form,
        'question_formset': question_formset
    }
    return render(request, 'trainer/create_quiz.html', context)

@login_required
@user_passes_test(is_trainer)
def manage_quizzes(request):
    quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    context = {'quizzes': quizzes}
    return render(request, 'trainer/manage_quizzes.html', context)

@login_required
@user_passes_test(is_trainer)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('trainer:manage_quizzes')
    else:
        form = QuizForm(instance=quiz)
    
    questions = quiz.questions.all()
    context = {'form': form, 'quiz': quiz, 'questions': questions}
    return render(request, 'trainer/edit_quiz.html', context)

@login_required
@user_passes_test(is_trainer)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully!')
    return redirect('trainer:manage_quizzes')

@login_required
@user_passes_test(is_trainer)
def manage_students(request):
    students = User.objects.filter(
        student_profile__assigned_trainer=request.user
    ).select_related('student_profile')
    
    # Get all students without trainer
    unassigned_students = User.objects.filter(
        student_profile__assigned_trainer__isnull=True,
        is_staff=False,
        is_superuser=False
    ).select_related('student_profile')
    
    context = {
        'students': students,
        'unassigned_students': unassigned_students
    }
    return render(request, 'trainer/manage_students.html', context)

@login_required
@user_passes_test(is_trainer)
def assign_student(request, student_id):
    student = get_object_or_404(User, id=student_id)
    
    if hasattr(student, 'student_profile'):
        student.student_profile.assigned_trainer = request.user
        student.student_profile.save()
        messages.success(request, f'{student.get_full_name()} has been assigned to you.')
    else:
        messages.error(request, 'Invalid student.')
    
    return redirect('trainer:manage_students')

@login_required
@user_passes_test(is_trainer)
def toggle_student_status(request, student_id):
    student = get_object_or_404(User, id=student_id)
    
    if hasattr(student, 'student_profile') and student.student_profile.assigned_trainer == request.user:
        profile = student.student_profile
        profile.is_active = not profile.is_active
        profile.save()
        
        status = 'activated' if profile.is_active else 'deactivated'
        messages.success(request, f'{student.get_full_name()} has been {status}.')
    else:
        messages.error(request, 'You can only manage your assigned students.')
    
    return redirect('trainer:manage_students')

@login_required
@user_passes_test(is_trainer)
def student_performance(request, student_id):
    student = get_object_or_404(User, id=student_id)
    
    # Check if trainer manages this student
    if hasattr(student, 'student_profile'):
        if student.student_profile.assigned_trainer != request.user:
            messages.error(request, 'You can only view performance of your assigned students.')
            return redirect('trainer:manage_students')
    
    # Get overall progress
    overall_progress = OverallProgress.objects.filter(student=student).first()
    
    # Get daily progress (last 30 days)
    daily_progress = DailyProgress.objects.filter(student=student).order_by('-date')[:30]
    
    # Get quiz attempts
    attempts = QuizAttempt.objects.filter(
        student=student,
        status='completed'
    ).select_related('quiz').order_by('-end_time')[:20]
    
    context = {
        'student': student,
        'overall_progress': overall_progress,
        'daily_progress': daily_progress,
        'attempts': attempts
    }
    return render(request, 'trainer/student_performance.html', context)