from django import forms
from .models import News, Disciplines


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

class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Disciplines
        fields = ['name', 'image']
        labels = {
            'name': 'Название дисциплины',
            'image': 'Обложка (картинка)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'arcade-input', 'placeholder': 'Например: CS2, Dota 2...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'arcade-file-input'}),
        }