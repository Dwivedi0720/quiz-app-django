from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import StudentProfile, TrainerProfile
from .forms import (
    StudentRegistrationForm,
    TrainerRegistrationForm,
    UserProfileForm
)

# =====================================
# STUDENT REGISTRATION
# =====================================
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.save()   # ✅ SIGNAL CREATES StudentProfile

            # ✅ UPDATE EXISTING PROFILE (DO NOT CREATE AGAIN)
            profile = user.student_profile
            profile.phone = form.cleaned_data.get('phone', '')
            profile.date_of_birth = form.cleaned_data.get('date_of_birth')
            profile.is_active = True
            profile.save()

            messages.success(
                request,
                'Student registered successfully! Please login.'
            )
            return redirect('accounts:login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'Student'
    })


# =====================================
# TRAINER REGISTRATION
# =====================================
def register_trainer(request):
    if request.method == 'POST':
        form = TrainerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            user.is_staff = True
            user.is_active = True
            user.is_superuser = False
            user.save()   # ✅ SIGNAL CREATES TrainerProfile

            # ✅ UPDATE EXISTING PROFILE
            trainer_profile = user.trainer_profile
            trainer_profile.phone = form.cleaned_data.get('phone', '')
            trainer_profile.specialization = form.cleaned_data.get('specialization', '')
            trainer_profile.save()

            messages.success(
                request,
                'Trainer registered successfully! Please login.'
            )
            return redirect('accounts:login')
    else:
        form = TrainerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'Trainer'
    })


# =====================================
# LOGIN
# =====================================
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # 🚫 BLOCK DEACTIVATED STUDENTS
            if not user.is_staff and not user.is_superuser:
                if hasattr(user, 'student_profile') and not user.student_profile.is_active:
                    messages.error(
                        request,
                        'Your account has been deactivated. Please contact your trainer.'
                    )
                    return redirect('accounts:login')

            login(request, user)

            # ROLE BASED REDIRECT
            if user.is_superuser:
                return redirect('/admin/')
            elif user.is_staff:
                return redirect('trainer:dashboard')
            else:
                return redirect('progress:dashboard')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# =====================================
# LOGOUT
# =====================================
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# =====================================
# PROFILE UPDATE
# =====================================
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

            # STUDENT PROFILE
            if hasattr(request.user, 'student_profile'):
                profile = request.user.student_profile
                profile.phone = request.POST.get('phone', '')
                profile.save()

            # TRAINER PROFILE
            elif hasattr(request.user, 'trainer_profile'):
                profile = request.user.trainer_profile
                profile.phone = request.POST.get('phone', '')
                profile.specialization = request.POST.get('specialization', '')
                profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form
    })
