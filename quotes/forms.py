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
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем источники, у которых меньше 3 цитат
        sources_with_less_than_3_quotes = Source.objects.annotate(
            quote_count=models.Count('quotes')
        ).filter(quote_count__lt=3)
        
        self.fields['source'].queryset = sources_with_less_than_3_quotes