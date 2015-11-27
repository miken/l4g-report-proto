from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import Survey


class SurveyList(ListView):
    model = Survey


class SurveyDetail(DetailView):
    model = Survey
