from django.contrib import admin
from .models import Question, Answer, Tag, Document

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'date_added')
    search_fields = ('text',)
    inlines = [AnswerInline]
    filter_horizontal = ('tags',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'correct')
    list_filter = ('correct', 'question')
    search_fields = ('text', 'question__text')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')