from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import Select2MultipleWidget
from django.forms import inlineformset_factory
from .models import Question, Answer, Tag, Document

class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()

    class Meta:
        model = Question
        fields = ['text', 'tags']
        widgets = {
            'tags': Select2MultipleWidget(attrs={
                'data-tags': 'true',
                'data-placeholder': 'Выберите или создайте метки',
                'data-allow-clear': 'true',
                'style': 'width: 100%;'
            }),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'correct']

AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm, extra=1, can_delete=True)

class DocumentForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if not file:
            raise ValidationError("Пожалуйста, выберите файл для загрузки.")
        if file.size > 5 * 1024 * 1024:  # Ограничение размера файла в 5 МБ
            raise ValidationError("Файл слишком большой (максимум 5 МБ).")
        return file

    class Meta:
        model = Document
        fields = ['title', 'file', 'tags']
        widgets = {
            'tags': Select2MultipleWidget(attrs={
                'data-tags': 'true',
                'data-placeholder': 'Выберите или создайте метки',
                'data-allow-clear': 'true',
                'style': 'width: 100%;'
            }),
        }
