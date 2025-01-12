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
from django.db.models import Exists, OuterRef
from django.db.models import Q, F, Value, BooleanField, Case, When
from django.contrib import messages
import requests


# Инициализация IDS
ids = IDS()

def block_ip(ip):
    requests.post('http://127.0.0.1:5000/block_ip', json={'ip': ip, 'duration': 5})

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
    all_tags = Tag.objects.all()
    return render(request, 'dashboard/questions.html', {
        'questions': questions,
        'current_page': 'questions',
        "all_tags": all_tags,
    })


@login_required
def documents(request):
    documents = Document.objects.order_by("id")
    return render(request, "dashboard/documents.html", {"documents": documents})

@login_required
def edit_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    all_tags = Tag.objects.all()

    if request.method == "POST":
        document.title = request.POST.get("document_title")
        document.description = request.POST.get("document_description")
        if "document_file" in request.FILES:
            document.file = request.FILES["document_file"]
        selected_tags = [tag for tag_id, tag in enumerate(all_tags) if f"tag_{tag.id}" in request.POST]
        document.tags.set(selected_tags)
        document.save()
        return redirect("documents")

    return render(request, "dashboard/edit_document.html", {"document": document, "all_tags": all_tags})


@login_required
def create_question(request):
    all_tags = Tag.objects.all()  # Получить все теги

    if request.method == "POST":
        # Создание нового вопроса
        question_text = request.POST.get("question_text", "").strip()
        if not question_text:
            messages.error(request, "Текст вопроса не может быть пустым.")
            return redirect("create_question")

        question = Question.objects.create(text=question_text)

        # Добавление тегов
        selected_tags = request.POST.getlist("tags")
        question.tags.set(selected_tags)

        # Добавление новых ответов
        new_answers = request.POST.getlist("new_answers[]")
        new_correct_flags = request.POST.getlist("new_correct_answers[]")
        for index, text in enumerate(new_answers):
            correct = new_correct_flags[index] if index < len(new_correct_flags) else "false"
            Answer.objects.create(
                question=question,
                text=text.strip(),
                correct=(correct == "true")
            )

        messages.success(request, "Вопрос успешно создан.")
        return redirect("questions")

    return render(request, "dashboard/create_question.html", {
        "all_tags": all_tags,
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
    all_tags = Tag.objects.all()

    # Разделение активных и неактивных тегов
    all_tags = Tag.objects.annotate(
        is_active=Exists(question.tags.filter(id=OuterRef('id')))
    ).order_by('-is_active', 'name')  # Сначала активные, затем по алфавиту

    if request.method == "POST":
        # Удаление ответов
        deleted_answers = request.POST.get("deleted_answers", "").split(",")
        for answer_id in deleted_answers:
            if answer_id:
                Answer.objects.filter(id=answer_id).delete()

        # Обновление текста вопроса
        question_text = request.POST.get("question_text", "").strip()
        if question_text:
            question.text = question_text
        question.save()

        # Обновление тегов
        selected_tags = request.POST.getlist("tags")
        question.tags.set(selected_tags)

        # Обновление существующих ответов
        for answer in answers:
            answer_text = request.POST.get(f"answer_text_{answer.id}", "").strip()
            answer_correct = f"answer_correct_{answer.id}" in request.POST
            if answer_text:
                answer.text = answer_text
                answer.correct = answer_correct
                answer.save()

        # Добавление новых ответов
        new_answers = request.POST.getlist("new_answers[]")
        new_correct_flags = request.POST.getlist("new_correct_answers[]")
        for index, text in enumerate(new_answers):
            correct = new_correct_flags[index] if index < len(new_correct_flags) else "false"
            Answer.objects.create(
                question=question,
                text=text.strip(),
                correct=(correct == "true")
            )

        # Проверка: как минимум два ответа
        updated_answers = question.answers.all()
        if len(updated_answers) < 2:
            messages.error(request, "У вопроса должно быть как минимум два ответа.")
            return render(request, "dashboard/edit_question.html", {
                "question": question,
                "answers": answers,
                "all_tags": all_tags,
            })

        # Проверка: минимум один ответ верный
        if not updated_answers.filter(correct=True).exists():
            messages.error(request, "У вопроса должен быть как минимум один верный ответ.")
            return render(request, "dashboard/edit_question.html", {
                "question": question,
                "answers": answers,
                "all_tags": all_tags,
            })

        messages.success(request, "Изменения успешно сохранены.")
        return redirect("questions")

    return render(request, "dashboard/edit_question.html", {
        "question": question,
        "answers": answers,
        "all_tags": all_tags,
    })