from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.forms import formset_factory

from accounts.models import StudentProfile
from quiz.models import Quiz, Question, QuizAttempt
from progress.models import DailyProgress, OverallProgress
from .forms import QuizForm, QuestionForm


# ==============================
# TRAINER CHECK
# ==============================
def is_trainer(user):
    return user.is_staff and not user.is_superuser


# ==============================
# TRAINER DASHBOARD
# ==============================
@login_required
@user_passes_test(is_trainer)
def dashboard(request):
    trainer = request.user

    students = User.objects.filter(
        student_profile__assigned_trainer=trainer
    )

    quizzes = Quiz.objects.filter(created_by=trainer)

    context = {
        'total_students': students.count(),
        'active_students': students.filter(student_profile__is_active=True).count(),
        'total_quizzes': quizzes.count(),
        'total_attempts': QuizAttempt.objects.filter(
            quiz__created_by=trainer
        ).count(),
        'recent_attempts': QuizAttempt.objects.filter(
            quiz__created_by=trainer,
            status='completed'
        ).select_related('student', 'quiz').order_by('-end_time')[:10]
    }

    return render(request, 'trainer/dashboard.html', context)


# ==============================
# CREATE QUIZ
# ==============================
@login_required
@user_passes_test(is_trainer)
def create_quiz(request):
    QuestionFormSet = formset_factory(
        QuestionForm,
        extra=5,
        max_num=20,
        can_delete=True
    )

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

            messages.success(request, 'Quiz created successfully!')
            return redirect('trainer:manage_quizzes')

    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet(prefix='questions')

    return render(request, 'trainer/create_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset
    })


# ==============================
# MANAGE QUIZZES
# ==============================
@login_required
@user_passes_test(is_trainer)
def manage_quizzes(request):
    quizzes = Quiz.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    return render(request, 'trainer/manage_quizzes.html', {
        'quizzes': quizzes
    })


# ==============================
# EDIT QUIZ
# ==============================
@login_required
@user_passes_test(is_trainer)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        created_by=request.user
    )

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('trainer:manage_quizzes')
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'trainer/edit_quiz.html', {
        'form': form,
        'quiz': quiz,
        'questions': quiz.questions.all()
    })


# ==============================
# DELETE QUIZ
# ==============================
@login_required
@user_passes_test(is_trainer)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        created_by=request.user
    )
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully!')
    return redirect('trainer:manage_quizzes')


# ==============================
# MANAGE STUDENTS
# ==============================
@login_required
@user_passes_test(is_trainer)
def manage_students(request):
    assigned_students = User.objects.filter(
        student_profile__assigned_trainer=request.user
    ).select_related('student_profile')

    unassigned_students = User.objects.filter(
        student_profile__assigned_trainer__isnull=True,
        is_staff=False,
        is_superuser=False
    ).select_related('student_profile')

    return render(request, 'trainer/manage_students.html', {
        'students': assigned_students,
        'unassigned_students': unassigned_students
    })


# ==============================
# ASSIGN STUDENT
# ==============================
@login_required
def assign_student(request, student_id):
    if not request.user.is_staff:
        return redirect('accounts:login')

    student_profile = get_object_or_404(StudentProfile, id=student_id)

    # ✅ assign logged-in trainer
    student_profile.assigned_trainer = request.user
    student_profile.is_active = True
    student_profile.save()

    messages.success(request, f"{student_profile.user.username} assigned successfully.")
    return redirect('trainer:manage_students')


# ==============================
# ACTIVATE / DEACTIVATE STUDENT
# ==============================
@login_required
@user_passes_test(is_trainer)
def toggle_student_status(request, student_id):
    student = get_object_or_404(User, id=student_id)

    if hasattr(student, 'student_profile') and \
       student.student_profile.assigned_trainer == request.user:

        profile = student.student_profile
        profile.is_active = not profile.is_active
        profile.save()

        status = 'activated' if profile.is_active else 'deactivated'
        messages.success(request, f'Student {status} successfully!')
    else:
        messages.error(request, 'Unauthorized action.')

    return redirect('trainer:manage_students')



# ==============================
# STUDENT PERFORMANCE
# ==============================
@login_required
@user_passes_test(is_trainer)
def student_performance(request, student_id):
    student = get_object_or_404(User, id=student_id)

    if hasattr(student, 'student_profile') and \
       student.student_profile.assigned_trainer != request.user:
        messages.error(request, 'You can only view your assigned students.')
        return redirect('trainer:manage_students')

    return render(request, 'trainer/student_performance.html', {
        'student': student,
        'overall_progress': OverallProgress.objects.filter(student=student).first(),
        'daily_progress': DailyProgress.objects.filter(student=student).order_by('-date')[:30],
        'attempts': QuizAttempt.objects.filter(
            student=student,
            status='completed'
        ).select_related('quiz').order_by('-end_time')[:20]
    })

@login_required
@user_passes_test(is_trainer)
def edit_questions(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        created_by=request.user
    )

    questions = quiz.questions.all().order_by('order')

    if request.method == 'POST':
        for q in questions:
            q.question_text = request.POST.get(f'question_{q.id}')
            q.option_a = request.POST.get(f'option_a_{q.id}')
            q.option_b = request.POST.get(f'option_b_{q.id}')
            q.option_c = request.POST.get(f'option_c_{q.id}')
            q.option_d = request.POST.get(f'option_d_{q.id}')
            q.correct_answer = request.POST.get(f'correct_{q.id}')
            q.time_limit = request.POST.get(f'time_{q.id}')
            q.save()

        messages.success(request, 'Questions updated successfully!')
        return redirect('trainer:manage_quizzes')

    return render(request, 'trainer/edit_questions.html', {
        'quiz': quiz,
        'questions': questions
    })
