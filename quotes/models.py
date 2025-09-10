from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['title', 'source_type']
        ordering = ['title']
    
    def __str__(self):
        return f"{self.get_source_type_display()}: {self.title}"
    
    def quote_count(self):
        return self.quotes.count()


class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты", unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes', verbose_name="Источник")
    weight = models.IntegerField(default=1, verbose_name="Вес (чем больше, тем чаще показывается)")
    likes = models.IntegerField(default=0, verbose_name="Лайки")
    dislikes = models.IntegerField(default=0, verbose_name="Дизлайки")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.text[:50]}... ({self.source.title})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)