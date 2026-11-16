from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Request(models.Model):
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


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reset_tokens',
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_reset_token'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]

    def is_valid(self):
        from django.utils import timezone
        return self.used_at is None and self.expires_at > timezone.now()