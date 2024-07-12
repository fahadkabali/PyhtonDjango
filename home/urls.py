from django.urls import path

from . import  views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('assessment_result/', views.assessment_result, name='assessment_result'),
    path('take_assessment/', views.take_assessment, name='take_assessment'),
    path('generate_certificate/', views.generate_certificate, name='generate_certificate'),


]