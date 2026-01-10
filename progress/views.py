from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DailyProgress, OverallProgress
from quiz.models import QuizAttempt
from django.db.models import Avg, Count
import json

@login_required
def dashboard(request):
    user = request.user
    
    # Get or create overall progress
    overall_progress, created = OverallProgress.objects.get_or_create(student=user)
    
    # Get daily progress (last 30 days)
    daily_progress = DailyProgress.objects.filter(student=user).order_by('-date')[:30]
    
    # Get recent quiz attempts
    recent_attempts = QuizAttempt.objects.filter(
        student=user,
        status='completed'
    ).select_related('quiz').order_by('-end_time')[:10]
    
    # Get available quizzes (not attempted)
    attempted_quiz_ids = QuizAttempt.objects.filter(student=user).values_list('quiz_id', flat=True)
    from quiz.models import Quiz
    available_quizzes = Quiz.objects.filter(is_active=True).exclude(id__in=attempted_quiz_ids)[:5]
    
    # Prepare chart data
    chart_dates = []
    chart_percentages = []
    chart_attempts = []
    
    for dp in reversed(list(daily_progress)):
        chart_dates.append(dp.date.strftime('%b %d'))
        chart_percentages.append(round(dp.average_percentage, 1))
        chart_attempts.append(dp.quizzes_attempted)
    
    context = {
        'overall_progress': overall_progress,
        'daily_progress': daily_progress,
        'recent_attempts': recent_attempts,
        'available_quizzes': available_quizzes,
        'chart_dates': json.dumps(chart_dates),
        'chart_percentages': json.dumps(chart_percentages),
        'chart_attempts': json.dumps(chart_attempts)
    }
    return render(request, 'progress/dashboard.html', context)