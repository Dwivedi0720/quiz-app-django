from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Quiz, Question, QuizAttempt, StudentAnswer
import json


# ==============================
# QUIZ LIST
# ==============================
@login_required
def quiz_list(request):
    if request.user.is_staff:
        quizzes = Quiz.objects.filter(created_by=request.user)
    else:
        quizzes = Quiz.objects.filter(is_active=True)
        attempted_quiz_ids = QuizAttempt.objects.filter(
            student=request.user
        ).values_list('quiz_id', flat=True)
        quizzes = quizzes.exclude(id__in=attempted_quiz_ids)

    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


# ==============================
# QUIZ DETAIL
# ==============================
@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    has_attempted = QuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz
    ).exists()

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'has_attempted': has_attempted
    })


# ==============================
# START QUIZ
# ==============================
@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.user.is_staff:
        messages.error(request, 'Only students can attempt quizzes.')
        return redirect('quiz:quiz_list')

    if hasattr(request.user, 'student_profile') and not request.user.student_profile.is_active:
        messages.error(request, 'Your account is deactivated.')
        return redirect('quiz:quiz_list')

    if QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists():
        messages.error(request, 'You have already attempted this quiz.')
        return redirect('quiz:quiz_list')

    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        status='in_progress',
        total_marks=quiz.total_marks
    )

    return redirect('quiz:take_quiz', attempt_id=attempt.id)


# ==============================
# TAKE QUIZ
# ==============================
@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        student=request.user
    )

    if attempt.status != 'in_progress':
        return redirect('quiz:quiz_result', attempt_id=attempt.id)

    questions = attempt.quiz.questions.all()

    return render(request, 'quiz/take_quiz.html', {
        'attempt': attempt,
        'questions': questions,
        'total_questions': questions.count()
    })


# ==============================
# SAVE ANSWER (AJAX)
# ==============================
@login_required
def submit_answer(request, attempt_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        student=request.user
    )

    if attempt.status != 'in_progress':
        return JsonResponse({'error': 'Quiz already completed'}, status=400)

    data = json.loads(request.body)
    question_id = data.get('question_id')
    selected_answer = data.get('answer')
    time_taken = data.get('time_taken', 0)

    question = get_object_or_404(
        Question,
        id=question_id,
        quiz=attempt.quiz
    )

    answer, _ = StudentAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={
            'selected_answer': selected_answer,
            'time_taken': time_taken
        }
    )

    return JsonResponse({
        'success': True,
        'is_correct': answer.is_correct
    })


# ==============================
# SUBMIT QUIZ
# ==============================
@login_required
def submit_quiz(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        student=request.user
    )

    if attempt.status != 'in_progress':
        return redirect('quiz:quiz_result', attempt_id=attempt.id)

    attempt.end_time = timezone.now()
    attempt.time_taken = int(
        (attempt.end_time - attempt.start_time).total_seconds()
    )
    attempt.status = 'completed'
    attempt.calculate_score()
    attempt.save()

    messages.success(request, 'Quiz submitted successfully!')
    return redirect('quiz:quiz_result', attempt_id=attempt.id)


# ==============================
# QUIZ RESULT ✅ FIXED
# ==============================
@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)

    if attempt.student != request.user and not request.user.is_staff:
        return redirect('quiz:quiz_list')

    if attempt.status != 'completed':
        return redirect('quiz:quiz_list')

    # ✅ FIX: ORM queries in VIEW, not template
    correct_count = attempt.answers.filter(is_correct=True).count()
    incorrect_count = attempt.answers.filter(is_correct=False).count()

    questions_with_answers = []
    for question in attempt.quiz.questions.all():
        answer = attempt.answers.filter(question=question).first()
        questions_with_answers.append({
            'question': question,
            'answer': answer
        })

    return render(request, 'quiz/quiz_result.html', {
        'attempt': attempt,
        'questions_with_answers': questions_with_answers,
        'is_passed': attempt.is_passed,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count
    })
