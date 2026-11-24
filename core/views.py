from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import RequestForm
from .models import Request
from accounts.decorators import role_required

# Главная страница
def index(request):
    return render(request, 'core/index.html')

# Служебный маршрут для проверки
def health(request):
    return JsonResponse({'status': 'ok', 'service': 'web'})

# Список заявок (для всех ролей)
@login_required
@role_required(['admin', 'executor', 'resident'])
def request_list_view(request):
    if request.user.role == 'resident':
        # Житель видит только свои заявки
        requests = Request.objects.filter(resident=request.user).order_by('-created_at')
    elif request.user.role == 'executor':
        # Исполнитель видит новые заявки и те, что взял сам
        requests = Request.objects.filter(
            models.Q(status='new') | models.Q(executor=request.user)
        ).order_by('-created_at')
    else:
        # Админ видит все заявки
        requests = Request.objects.all().order_by('-created_at')
    
    return render(request, 'core/request_list.html', {'requests': requests})

# Создание заявки (только для жителя)
@login_required
@role_required(['resident'])
def create_request_view(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.resident = request.user
            req.save()
            return redirect('core:request_list')
    else:
        form = RequestForm()
    return render(request, 'core/create_request.html', {'form': form})

# Приступить к работе (исполнитель)
@login_required
@role_required(['executor'])
def take_request_view(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    if req.status == 'new':
        req.status = 'in_progress'
        req.executor = request.user
        req.save()
    return redirect('core:request_list')

# Завершить работу (исполнитель)
@login_required
@role_required(['executor'])
def complete_request_view(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    if req.executor == request.user and req.status == 'in_progress':
        req.status = 'done'
        req.save()
    return redirect('core:request_list')
import json
from django.http import JsonResponse
from .agent_client import ask_agent, AgentError
from .models import AIMessage

@login_required
def agent_page(request):
    return render(request, 'core/agent.html')

@login_required
def agent_send(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    data = json.loads(request.body)
    text = (data.get('message') or '').strip()
    if not text or len(text) > 2000:
        return JsonResponse({'error': 'Сообщение пустое или длиннее 2000 символов'}, status=400)

    AIMessage.objects.create(user=request.user, role='user', content=text)
    
    history_rows = AIMessage.objects.filter(user=request.user).order_by('-created_at')[:10]
    history = [{'role': m.role, 'content': m.content} for m in reversed(history_rows)]

    try:
        reply = ask_agent(history, text)
    except AgentError as e:
        return JsonResponse({'error': str(e)}, status=502)

    AIMessage.objects.create(user=request.user, role='assistant', content=reply)
    return JsonResponse({'reply': reply})