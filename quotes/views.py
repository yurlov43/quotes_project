from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.views.decorators.http import require_POST
import random
from .models import Quote, Source
from .forms import QuoteForm, SourceForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError

def random_quote(request):
    # Получаем случайную цитату с учетом веса
    quotes = Quote.objects.all()
    if quotes.exists():
        weights = [quote.weight for quote in quotes]
        random_quote = random.choices(quotes, weights=weights, k=1)[0]
        
        # Увеличиваем счетчик просмотров
        random_quote.views += 1
        random_quote.save()
        
        context = {
            'quote': random_quote,
        }
    else:
        context = {'quote': None}
    
    return render(request, 'quotes/random_quote.html', context)

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            try:
                quote = form.save(commit=False)
                quote.full_clean()  # Дополнительная валидация
                quote.save()
                return redirect('random_quote')
            except ValidationError as e:
                # Обрабатываем ошибки валидации из модели
                for field, errors in e.error_dict.items():
                    for error in errors:
                        if field == '__all__':
                            form.add_error(None, error)
                        else:
                            form.add_error(field, error)
            except IntegrityError as e:
                # Обрабатываем ошибки уникальности из базы данных
                if 'unique' in str(e).lower():
                    form.add_error('text', 'Такая цитата уже существует в базе!')
                else:
                    form.add_error(None, f'Ошибка базы данных: {e}')
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})

def add_source(request):
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_quote')
    else:
        form = SourceForm()
    
    return render(request, 'quotes/add_source.html', {'form': form})

def popular_quotes(request):
    # 10 самых популярных цитат по лайкам
    popular_by_likes = Quote.objects.order_by('-likes')[:10]
    
    # 10 самых популярных по соотношению лайков/дизлайков
    popular_by_ratio = Quote.objects.annotate(
        total_votes=F('likes') + F('dislikes')
    ).filter(total_votes__gt=0).annotate(
        ratio=(F('likes') * 100) / F('total_votes')
    ).order_by('-ratio')[:10]
    
    # 10 самых просматриваемых
    most_viewed = Quote.objects.order_by('-views')[:10]
    
    context = {
        'popular_by_likes': popular_by_likes,
        'popular_by_ratio': popular_by_ratio,
        'most_viewed': most_viewed,
    }
    
    return render(request, 'quotes/popular_quotes.html', context)

@require_POST
def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    action = request.POST.get('action')
    
    if action == 'like':
        quote.likes += 1
    elif action == 'dislike':
        quote.dislikes += 1
    
    quote.save()
    
    return JsonResponse({
        'likes': quote.likes,
        'dislikes': quote.dislikes,
        'popularity': quote.popularity()
    })