from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Question, Document, Tag
from .forms import QuestionForm, AnswerFormSet, DocumentForm
from ids_core import IDS
from astra_v2.context_processors import check_user_access  # Импорт функции из context_processors.py
from django.db.models import Prefetch
from .models import Question, Answer
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory


# Инициализация IDS
ids = IDS()


def check_access_or_redirect(request):
    """
    Проверяет доступ пользователя через функцию check_user_access.
    Если доступа нет, перенаправляет на главную страницу.
    """
    access = check_user_access(request).get('has_service_access', False)
    if not access:
        messages.error(request, "У вас нет доступа к этому разделу.")
        return redirect('home')


@login_required
def dashboard(request):
    access_redirect = check_access_or_redirect(request)
    if access_redirect:
        return access_redirect
    return render(request, 'dashboard/dashboard.html', {
        'current_page': 'dashboard'
    })


@login_required
def questions(request):
    access_redirect = check_access_or_redirect(request)
    if access_redirect:
        return access_redirect

    query = request.GET.get('q')
    question_queryset = Question.objects.prefetch_related(
        Prefetch('answers', queryset=Answer.objects.all())
    )
    questions = (
        question_queryset.filter(
            Q(text__icontains=query) | Q(answers__text__icontains=query)
        ).distinct()
        if query else question_queryset
    )
    return render(request, 'dashboard/questions.html', {
        'questions': questions,
        'current_page': 'questions'
    })


@login_required
def documents(request):
    access_redirect = check_access_or_redirect(request)
    if access_redirect:
        return access_redirect

    query = request.GET.get('q')
    selected_ids = request.GET.get('selected_ids', '').split(',')
    documents = (
        Document.objects.filter(
            Q(title__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()
        if query else Document.objects.all()
    )
    return render(request, 'dashboard/documents.html', {
        'documents': documents,
        'selected_ids': selected_ids,
        'current_page': 'documents'
    })


@login_required
def create_question(request):
    access_redirect = check_access_or_redirect(request)
    if access_redirect:
        return access_redirect

    if request.method == 'POST':
        tags = request.POST.getlist('tags')
        new_tags = []
        for tag in tags:
            if not tag.isdigit():
                tag_obj, created = Tag.objects.get_or_create(name=tag)
                new_tags.append(str(tag_obj.id))
            else:
                new_tags.append(tag)

        request.POST = request.POST.copy()
        request.POST.setlist('tags', new_tags)

        form = QuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            ids.log_event(request.user.username, "Создание нового вопроса")
            return redirect('dashboard')
    else:
        form = QuestionForm()
        formset = AnswerFormSet()

    return render(request, 'dashboard/create_question.html', {
        'form': form,
        'formset': formset,
        'current_page': 'create_question'
    })


@login_required
def upload_document(request):
    access_redirect = check_access_or_redirect(request)
    if access_redirect:
        return access_redirect

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            ids.log_event(request.user.username, "Загрузка документа")
            return redirect('documents')
    else:
        form = DocumentForm()
    return render(request, 'dashboard/upload_document.html', {
        'form': form,
        'current_page': 'upload_document'
    })

@login_required
def edit_question(request, pk):
    # Получение вопроса и связанных данных
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all()
    all_tags = Tag.objects.all()  # Получить все доступные теги

    if request.method == "POST":
        # Обновление текста вопроса
        question_text = request.POST.get("question_text", "").strip()
        if question_text:
            question.text = question_text
        question.save()

        # Обновление тегов
        selected_tags = []
        for tag in all_tags:
            if request.POST.get(f"tag_{tag.id}", None):
                selected_tags.append(tag)
        question.tags.set(selected_tags)

        # Обновление ответов
        for answer in answers:
            answer_text = request.POST.get(f"answer_text_{answer.id}", "").strip()
            answer_correct = request.POST.get(f"answer_correct_{answer.id}", None) is not None
            if answer_text:  # Если текст ответа не пустой
                answer.text = answer_text
                answer.correct = answer_correct
                answer.save()

        return redirect("questions")

    # Рендер страницы редактирования
    return render(request, "dashboard/edit_question.html", {
        "question": question,
        "answers": answers,
        "all_tags": all_tags,
    })