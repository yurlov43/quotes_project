from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Source(models.Model):
    SOURCE_TYPES = [
        ('movie', 'Фильм'),
        ('book', 'Книга'),
        ('series', 'Сериал'),
        ('game', 'Игра'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name="Тип")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['title', 'source_type']
        ordering = ['title']
    
    def __str__(self):
        return f"{self.get_source_type_display()}: {self.title} ({self.year})"
    
    def quote_count(self):
        return self.quotes.count()


class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты", unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes', verbose_name="Источник")
    # ... остальные поля ...
    
    class Meta:
        ordering = ['-created_at']
    
    def clean(self):
        """Валидация на уровне модели с регистронезависимой проверкой"""
        # Проверка, что у источника не больше 3 цитат
        if self.pk is None:  # Новая запись
            if Quote.objects.filter(source=self.source).count() >= 3:
                raise ValidationError(f"У источника '{self.source.title}' уже максимальное количество цитат (3)")
        
        # Регистронезависимая проверка на дубликат текста
        if self.text:
            # Нормализуем текст: убираем лишние пробелы и приводим к нижнему регистру
            normalized_text = self.text.strip().lower()
            
            # Ищем существующие цитаты с таким же нормализованным текстом
            existing_quotes = Quote.objects.all()
            if self.pk:
                existing_quotes = existing_quotes.exclude(pk=self.pk)
            
            for existing_quote in existing_quotes:
                if existing_quote.text.strip().lower() == normalized_text:
                    raise ValidationError("Такая цитата уже существует в базе!")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем полную валидацию
        super().save(*args, **kwargs)