from django import forms
from .models import Quote, Source
from django.db import models

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['title', 'source_type', 'year']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'source_type': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Введите текст цитаты...'
            }),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1,
                'value': 1
            }),
        }
        error_messages = {
            'text': {
                'unique': "Такая цитата уже существует!",
            },
        }
    
    def clean_text(self):
        """Регистронезависимая проверка текста цитаты"""
        text = self.cleaned_data.get('text')
        
        if text:
            # Нормализуем текст для сравнения
            normalized_text = text.strip().lower()
            
            # Проверяем на дубликаты (регистронезависимо)
            queryset = Quote.objects.all()
            
            # Если редактируем существующую запись, исключаем её из проверки
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            # Проверяем каждую существующую цитату
            for existing_quote in queryset:
                if existing_quote.text.strip().lower() == normalized_text:
                    raise forms.ValidationError(
                        f"Цитата '{existing_quote.text[:50]}...' уже существует "
                        f"(источник: {existing_quote.source.title})"
                    )
        
        return text
    
    def clean(self):
        """Дополнительная валидация"""
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        
        # Проверка ограничения в 3 цитаты на источник (только для новых записей)
        if source and not self.instance.pk:
            if Quote.objects.filter(source=source).count() >= 3:
                raise forms.ValidationError(
                    f"У источника '{source.title}' уже максимальное количество цитат (3). "
                    f"Выберите другой источник."
                )
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем источники, у которых меньше 3 цитат
        sources_with_less_than_3_quotes = Source.objects.annotate(
            quote_count=models.Count('quotes')
        ).filter(quote_count__lt=3)
        
        self.fields['source'].queryset = sources_with_less_than_3_quotes
        
        # Добавляем CSS класс для ошибок
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' is-invalid'