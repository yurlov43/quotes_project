from django.contrib import admin
from .models import Source, Quote


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_type', 'quote_count', 'created_at']
    list_filter = ['source_type', 'created_at']
    search_fields = ['title']
    ordering = ['title']
    readonly_fields = ['created_at']
    
    def quote_count(self, obj):
        return obj.quote_count()
    quote_count.short_description = 'Количество цитат'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'source', 'weight', 'likes', 'dislikes', 'views', 'created_at']
    list_filter = ['source', 'source__source_type', 'created_at']
    search_fields = ['text', 'source__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('text', 'source', 'weight')
        }),
        ('Статистика', {
            'fields': ('likes', 'dislikes', 'views')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст цитаты'
