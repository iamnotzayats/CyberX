from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, template_name='news.html', context={'page_title': 'Home'})
