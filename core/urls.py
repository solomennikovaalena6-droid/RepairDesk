from django.urls import path
from . import views
from .api_views import RequestListCreateAPI, RequestDetailAPI
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'core'

urlpatterns = [
    # --- Обычные страницы ---
    path('', views.index, name='index'),
    path('health/', views.health, name='health'),
    path('requests/', views.request_list_view, name='request_list'),
    path('requests/create/', views.create_request_view, name='create_request'),
    path('requests/take/<int:request_id>/', views.take_request_view, name='take_request'),
    path('requests/complete/<int:request_id>/', views.complete_request_view, name='complete_request'),

    # --- ИИ-помощник ---
    path('agent/', views.agent_page, name='agent_page'),
    path('agent/send/', views.agent_send, name='agent_send'),

    # --- API ---
    path('api/requests/', RequestListCreateAPI.as_view(), name='api-request-list'),
    path('api/requests/<int:pk>/', RequestDetailAPI.as_view(), name='api-request-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]