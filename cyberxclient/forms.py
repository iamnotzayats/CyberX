from django import forms
from .models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'categories', 'badge']

        labels = {
            'title': 'Заголовок',
            'content': 'Текст новости',
            'categories': 'Категории',
            'badge': 'Бейджи',
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'arcade-input', 'placeholder': 'Введите заголовок...'}),
            'content': forms.Textarea(
                attrs={'class': 'arcade-textarea', 'placeholder': 'Текст новости...', 'rows': 10}),
            'categories': forms.SelectMultiple(attrs={'class': 'arcade-select'}),
            'badge': forms.SelectMultiple(attrs={'class': 'arcade-select'}),
        }