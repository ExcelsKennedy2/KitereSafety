from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import UserProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Kitere Safety System.')
            return redirect('report_incident')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # return redirect('core:index')
        return redirect('report_incident')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on role
                if user.role == 'responder':
                    return redirect('dashboard')
                elif user.role == 'admin':
                    return redirect('admin:index')
                else:
                    # return redirect('core:index')
                    return redirect('report_incident')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    # return redirect('core:index')
    return redirect('login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')