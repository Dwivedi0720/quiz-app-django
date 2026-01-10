from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Quiz, Question, QuizAttempt, StudentAnswer
import json

@login_required
def quiz_list(request):
    if request.user.is_staff:
        quizzes = Quiz.objects.filter(created_by=request.user)
    else:
        quizzes = Quiz.objects.filter(is_active=True)
        # Filter out already attempted quizzes
        attempted_quiz_ids = QuizAttempt.objects.filter(
            student=request.user
        ).values_list('quiz_id', flat=True)
        quizzes = quizzes.exclude(id__in=attempted_quiz_ids)
    
    context = {'quizzes': quizzes}
    return render(request, 'quiz/quiz_list.html', context)

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if student has already attempted
    has_attempted = QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists()
    
    context = {
        'quiz': quiz,
        'has_attempted': has_attempted
    }
    return render(request, 'quiz/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if student
    if request.user.is_staff:
        messages.error(request, 'Only students can attempt quizzes.')
        return redirect('quiz:quiz_list')
    
    # Check if student is active
    if hasattr(request.user, 'student_profile') and not request.user.student_profile.is_active:
        messages.error(request, 'Your account is deactivated. Contact your trainer.')
        return redirect('quiz:quiz_list')
    
    # Check if already attempted
    if QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists():
        messages.error(request, 'You have already attempted this quiz.')
        return redirect('quiz:quiz_list')
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        status='in_progress',
        total_marks=quiz.total_marks
    )
    
    return redirect('quiz:take_quiz', attempt_id=attempt.id)

@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status != 'in_progress':
        messages.error(request, 'This quiz attempt has ended.')
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    questions = attempt.quiz.questions.all()
    
    context = {
        'attempt': attempt,
        'questions': questions,
        'total_questions': questions.count()
    }
    return render(request, 'quiz/take_quiz.html', context)

@login_required
def submit_answer(request, attempt_id):
    if request.method == 'POST':
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
        
        if attempt.status != 'in_progress':
            return JsonResponse({'error': 'Quiz already completed'}, status=400)
        
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_answer = data.get('answer')
        time_taken = data.get('time_taken', 0)
        
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
        
        # Save or update answer
        answer, created = StudentAnswer.objects.update_or_create(
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
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def submit_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status != 'in_progress':
        messages.error(request, 'This quiz has already been submitted.')
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    # Calculate total time
    time_taken = (timezone.now() - attempt.start_time).total_seconds()
    attempt.time_taken = int(time_taken)
    attempt.end_time = timezone.now()
    attempt.status = 'completed'
    attempt.calculate_score()
    attempt.save()
    
    messages.success(request, 'Quiz submitted successfully!')
    return redirect('quiz:quiz_result', attempt_id=attempt.id)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Check permission
    if attempt.student != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this result.')
        return redirect('quiz:quiz_list')
    
    if attempt.status != 'completed':
        messages.error(request, 'Quiz not yet completed.')
        return redirect('quiz:quiz_list')
    
    questions_with_answers = []
    for question in attempt.quiz.questions.all():
        try:
            answer = StudentAnswer.objects.get(attempt=attempt, question=question)
        except StudentAnswer.DoesNotExist:
            answer = None
        
        questions_with_answers.append({
            'question': question,
            'answer': answer
        })
    
    context = {
        'attempt': attempt,
        'questions_with_answers': questions_with_answers,
        'is_passed': attempt.is_passed
    }
    return render(request, 'quiz/quiz_result.html', context)