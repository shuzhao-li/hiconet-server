from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('submit/<slug:analysis>/', views.submit_view, name='submit'),
    path('status/<uuid:task_id>', views.status_view, name='status'),
    path('result/<uuid:task_id>/', views.result_view, name='result'),
]
