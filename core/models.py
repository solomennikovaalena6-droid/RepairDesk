from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Request(models.Model):
    # 1. Константы для статусов (должны быть ВНУТРИ класса)
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_DONE, 'Выполнена'),
        (STATUS_CANCELLED, 'Отклонена'),
    ]

    # 2. Поля заявки
    resident_name = models.CharField('Имя жителя', max_length=100, default='')
    phone = models.CharField('Телефон', max_length=20, default='')
    floor = models.CharField('Этаж', max_length=10, default='')
    
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resident_requests',
        verbose_name='Житель',
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='executor_requests',
        verbose_name='Исполнитель',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        verbose_name='Категория',
    )
    description = models.TextField('Описание')
    photo = models.ImageField('Фото', upload_to='requests/', blank=True)
    room = models.CharField('Комната', max_length=50)
    status = models.CharField(
        'Статус', max_length=20,
        choices=STATUS_CHOICES, default=STATUS_NEW,
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        db_table = 'requests'
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка {self.id} - {self.room}'


class Comment(models.Model):
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Заявка',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField('Текст')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class AIHelper(models.Model):
    request = models.OneToOneField(
        Request, on_delete=models.CASCADE,
        related_name='ai_helper', verbose_name='Заявка',
    )
    predicted_category = models.CharField(
        'Категория (ИИ)', max_length=100, blank=True)
    hint = models.TextField('Подсказка', blank=True)

    class Meta:
        db_table = 'ai_helpers'
        verbose_name = 'ИИ-подсказка'
        verbose_name_plural = 'ИИ-подсказки'


class AIMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_messages',
    )
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']