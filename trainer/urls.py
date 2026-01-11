from django.urls import path
from . import views

app_name = 'trainer'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/manage/', views.manage_quizzes, name='manage_quizzes'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('students/', views.manage_students, name='manage_students'),
    path('students/<int:student_id>/assign/', views.assign_student, name='assign_student'),
    path('students/<int:student_id>/toggle/', views.toggle_student_status, name='toggle_student_status'),
    path('students/<int:student_id>/performance/', views.student_performance, name='student_performance'),
    path(
    'quiz/<int:quiz_id>/questions/edit/',
    views.edit_questions,
    name='edit_questions'
)
]