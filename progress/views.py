from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DailyProgress, OverallProgress
from quiz.models import QuizAttempt, Quiz
import json


@login_required
def dashboard(request):
    user = request.user

    # ✅ Redirect trainers properly
    if hasattr(user, 'trainer_profile'):
        return redirect('trainer:dashboard')

    # ✅ Student dashboard logic
    overall_progress, _ = OverallProgress.objects.get_or_create(student=user)

    daily_progress = DailyProgress.objects.filter(
        student=user
    ).order_by('-date')[:30]

    recent_attempts = QuizAttempt.objects.filter(
        student=user,
        status='completed'
    ).select_related('quiz').order_by('-end_time')[:10]

    attempted_quiz_ids = QuizAttempt.objects.filter(
        student=user
    ).values_list('quiz_id', flat=True)

    available_quizzes = Quiz.objects.filter(
        is_active=True
    ).exclude(id__in=attempted_quiz_ids)[:5]

    chart_dates = []
    chart_percentages = []

    for dp in reversed(list(daily_progress)):
        chart_dates.append(dp.date.strftime('%b %d'))
        chart_percentages.append(round(dp.average_percentage, 1))

    context = {
        'overall_progress': overall_progress,
        'daily_progress': daily_progress,
        'recent_attempts': recent_attempts,
        'available_quizzes': available_quizzes,
        'chart_dates': json.dumps(chart_dates),
        'chart_percentages': json.dumps(chart_percentages),
    }

    return render(request, 'progress/dashboard.html', context)
