from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import StudentProfile, TrainerProfile
from .forms import StudentRegistrationForm, TrainerRegistrationForm, UserProfileForm

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            StudentProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                enrollment_number=f"ST{user.id:05d}"
            )
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('accounts:login')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Student'})

def register_trainer(request):
    if request.method == 'POST':
        form = TrainerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.save()
            
            TrainerProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                specialization=form.cleaned_data.get('specialization', ''),
                employee_id=f"TR{user.id:05d}"
            )
            
            messages.success(request, 'Trainer registration successful! You can now login.')
            return redirect('accounts:login')
    else:
        form = TrainerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'Trainer'})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if student is active
            if not user.is_staff and not user.is_superuser:
                if hasattr(user, 'student_profile') and not user.student_profile.is_active:
                    messages.error(request, 'Your account has been deactivated. Please contact your trainer.')
                    return redirect('accounts:login')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on role
            if user.is_superuser:
                return redirect('admin:index')
            elif user.is_staff:
                return redirect('trainer:dashboard')
            else:
                return redirect('progress:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            
            if hasattr(request.user, 'student_profile'):
                profile = request.user.student_profile
                profile.phone = request.POST.get('phone', '')
                profile.save()
            elif hasattr(request.user, 'trainer_profile'):
                profile = request.user.trainer_profile
                profile.phone = request.POST.get('phone', '')
                profile.specialization = request.POST.get('specialization', '')
                profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/profile.html', context)

