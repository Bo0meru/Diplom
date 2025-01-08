from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Question, Answer

# Обновление last_updated при изменении ответа
@receiver(post_save, sender=Answer)
@receiver(post_delete, sender=Answer)
def update_question_on_answer_change(sender, instance, **kwargs):
    if instance.question:
        instance.question.save()  # Это вызовет обновление last_updated

# Обновление last_updated при изменении меток
@receiver(m2m_changed, sender=Question.tags.through)
def update_question_on_tag_change(sender, instance, **kwargs):
    instance.save()  # Это вызовет обновление last_updated
