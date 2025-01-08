# # urls.py

# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
#     path('questions/new/', views.create_question, name='create_question'),
#     path('documents/upload/', views.upload_document, name='upload_document'),
#     path('documents/<int:pk>/edit/', views.edit_document, name='edit_document'),
#     path('documents/<int:pk>/', views.view_document, name='view_document'),
#     path('questions/', views.questions, name='questions'),
#     path('documents/', views.documents, name='documents'),
#     path('export_questions/', views.export_questions, name='export_questions'),
#     path('export_documents/', views.export_documents, name='export_documents'),
#     path('tags/', views.tag_list, name='tag_list'),
#     path('tags/autocomplete/', views.tag_autocomplete, name='tag_autocomplete'),
#     path('documents/preview/<int:pk>/', views.preview_document, name='preview_document'),
#     path('generate-report/', views.generate_report, name='generate_report'),
# ] 

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('questions/', views.questions, name='questions'),
    path('questions/new/', views.create_question, name='create_question'),
    path('documents/', views.documents, name='documents'),
    path("documents/<int:pk>/edit/", views.edit_document, name="edit_document"),
    path('questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('questions/create/', views.create_question, name='create_question'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
