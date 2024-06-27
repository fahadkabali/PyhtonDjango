

from django.urls import path, re_path
from . import  views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('assessment/', views.assessment_view, name='assessment'),
    path('results/', views.results_view, name="results")

    # # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]