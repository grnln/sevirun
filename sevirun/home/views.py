from django.shortcuts import render
from .models import DisplayCase, Article
from django.http import HttpResponse
from django.template import loader

def home(request):
    display_case = DisplayCase.objects.select_related('article').first()
    article_title = display_case.article.title if (display_case and getattr(display_case, 'article', None)) else None
    return render(request, 'home.html', {'article_title': article_title})