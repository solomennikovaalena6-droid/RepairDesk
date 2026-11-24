from django.contrib import admin
from django.contrib import admin
from .models import Category, Request

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'resident_name', 'room', 'status', 'created_at')