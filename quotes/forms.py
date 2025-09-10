from django import forms
from .models import Quote, Source
from django.db import models

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['title', 'source_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название источника...'}),
            'source_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        if not title:
            self.add_error('title', "Пожалуйста, введите название источника!")
        
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get('source_type')
        title = cleaned_data.get('title')
        
        if not source_type:
            self.add_error('source_type', 'Пожалуйста, выберите тип источника!')
        
        # Проверяем дубли только в рамках выбранного типа источника
        if source_type and title:
            normalized_text = title.strip().lower()
            for existing_source in Source.objects.filter(source_type=source_type):
                if existing_source.title.strip().lower() == normalized_text:
                    self.add_error('title', "Такой источник уже существует для выбранного типа!")
                    break
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['source_type'].required = False
        # Добавляем явно пустой пункт в начало списка choices.
        choices = list(self.fields['source_type'].choices)
        # Уберём возможную дублирующую пустую опцию по умолчанию
        choices = [(value, label) for value, label in choices if value != '']
        self.fields['source_type'].choices = [('', 'Выберите тип источника...')] + choices
        self.fields['title'].required = False

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите текст цитаты...'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        
        if text:
            normalized_text = text.strip().lower()
        
            for existing_quote in Quote.objects.all():
                if existing_quote.text.strip().lower() == normalized_text:
                    self.add_error('text', "Такая цитата уже существует в базе!")
                    break
        else:
            self.add_error('text', "Пожалуйста, введите текст цитаты!")
        
        return text
    
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        
        if not source:
            self.add_error('source', 'Пожалуйста, выберите источник!')
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['source'].required = False
        self.fields['source'].empty_label = "Выберите источник..."
        self.fields['text'].required = False

        # Фильтруем источники с менее чем 3 цитатами
        sources_with_less_than_3_quotes = Source.objects.annotate(
            quote_count=models.Count('quotes')
        ).filter(quote_count__lt=3)
        
        self.fields['source'].queryset = sources_with_less_than_3_quotes