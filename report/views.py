from django.views.generic import ListView
from .models import Survey


class SurveyList(ListView):
    model = Survey
