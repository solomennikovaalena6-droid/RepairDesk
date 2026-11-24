from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ForgotPasswordForm, ResetPasswordForm
from .decorators import role_required
from .models import PasswordResetToken, User
import secrets
import hashlib
from django.core.mail import send_mail
from django.urls import reverse

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна.')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        # Используем стандартную форму Django
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы вошли в систему.')
            return redirect('profile')
        else:
            messages.error(request, 'Неверные учётные данные. Проверьте логин и пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Request

@login_required
def profile_view(request):
    completed_count = 0
    if request.user.role == 'executor':
        completed_count = Request.objects.filter(executor=request.user, status='done').count()
    
    return render(request, 'accounts/profile.html', {'completed_count': completed_count})

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    # Все заявки
    requests = Request.objects.all().order_by('-created_at')
    
    # Статистика по исполнителям
    # Берем всех пользователей, у которых роль 'executor'
    executors = User.objects.filter(role='executor')
    
    # Для каждого исполнителя считаем выполненные заявки
    executors_stats = []
    for executor in executors:
        completed_count = Request.objects.filter(executor=executor, status='done').count()
        executors_stats.append({
            'username': executor.username,
            'email': executor.email,
            'completed_count': completed_count,
        })
    
    return render(request, 'accounts/admin_dashboard.html', {
        'requests': requests,
        'executors_stats': executors_stats,
    })

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                raw_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
                PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
                PasswordResetToken.objects.create(user=user, token_hash=hashed_token)
                reset_url = request.build_absolute_uri(reverse('reset_password', kwargs={'token': raw_token}))
                send_mail('Восстановление пароля', f'Ссылка: {reset_url}', None, [user.email], fail_silently=False)
            messages.success(request, 'Если аккаунт с таким email существует, письмо отправлено.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password_view(request, token):
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    reset_token = PasswordResetToken.objects.filter(token_hash=hashed_token, is_used=False).first()
    if not reset_token or not reset_token.is_valid():
        messages.error(request, 'Ссылка недействительна.')
        return redirect('login')
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Пароль изменён.')
            return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form})