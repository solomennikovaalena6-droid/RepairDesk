from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminRole
from .models import Request  # Импортируем модель заявки

class AdminRequestListAPI(APIView):
    # Указываем, что доступ только для авторизованных админов
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        # Получаем все заявки (только для админа)
        requests = Request.objects.all()
        # Формируем простой JSON-ответ
        data = [
            {
                "id": req.id,
                "room": req.room,
                "description": req.description,
                "status": req.status,
                "resident": req.resident.username if req.resident else None,
                "executor": req.executor.username if req.executor else None,
            }
            for req in requests
        ]
        return Response({"status": "ok", "requests": data})
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Request
from .serializers import RequestSerializer
from accounts.permissions import IsAdminRole

# Список и создание (GET, POST)
class RequestListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'resident':
            requests = Request.objects.filter(resident=request.user)
        else:
            requests = Request.objects.all()
        serializer = RequestSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != 'resident':
            return Response({"detail": "Только жители могут создавать заявки."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(resident=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Возвращаем 422 при ошибке валидации
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# Детали (GET, PUT, DELETE)
class RequestDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Request, pk=pk)

    def get(self, request, pk):
        req = self.get_object(pk)
        serializer = RequestSerializer(req)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        req = self.get_object(pk)
        serializer = RequestSerializer(req, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, pk):
        # Ищем заявку среди ВСЕХ заявок в базе
        req = get_object_or_404(Request, pk=pk)
        
        # Проверяем права: удалить может только админ или автор заявки
        if request.user.role != 'admin' and req.resident != request.user:
            return Response({"detail": "Нет прав на удаление."}, status=status.HTTP_403_FORBIDDEN)
        
        req.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)