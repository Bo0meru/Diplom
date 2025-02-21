from django.db import models

# models.py


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField(verbose_name="Текст вопроса")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions', verbose_name="Теги")

    class Meta:
        ordering = ['id']  # Сортировка по ID

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Вопрос")
    text = models.TextField(verbose_name="Текст ответа")
    correct = models.BooleanField(default=False, verbose_name="Правильный ответ?")

    def __str__(self):
        return self.text

from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название документа")
    description = models.TextField(verbose_name="Описание", blank=True)
    file = models.FileField(upload_to="documents/", verbose_name="Файл")
    tags = models.ManyToManyField(Tag, related_name="documents", verbose_name="Метки")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    def __str__(self):
        return self.title
