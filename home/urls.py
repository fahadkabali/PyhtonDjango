from django.urls import path

from . import  views

urlpatterns = [

    # The home page
    path('', views.index, name='index'),
    path('assessment_result/', views.assessment_result, name='assessment_result'),
    path('take_assessment/', views.take_assessment, name='take_assessment'),
    path('generate_certificate/', views.generate_certificate, name='generate_certificate'),
    path('search/', views.search_view, name='search'),
    path('question/<int:question_id>/', views.question_detail_view, name='question_detail'),
    path('assessment/history/', views.assessment_history, name='assessment_history'),

]


