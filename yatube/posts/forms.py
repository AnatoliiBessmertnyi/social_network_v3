from django import forms
from . models import Post



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Новый пост',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Введите текст своего поста',
            'group': 'Группа, к которой будет относиться пост',
        }
