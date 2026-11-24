from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['resident_name', 'phone', 'floor', 'room', 'category', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите проблему подробнее...'}),
        }
        labels = {
            'resident_name': 'Ваше имя',
            'phone': 'Номер телефона',
            'floor': 'Этаж',
            'room': 'Номер комнаты',
            'category': 'Категория проблемы',
            'description': 'Описание проблемы',
            'photo': 'Фото (необязательно)',
        }