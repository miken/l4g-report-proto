from django.contrib import admin
from .models import Survey, Question, Choice


class QuestionInline(admin.TabularInline):
    model = Question
    choice = 1


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'net_promoter_score')
    inlines = [QuestionInline]


class ChoiceInline(admin.TabularInline):
    model = Choice


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'nps', 'open_ended')
    inlines = [ChoiceInline]


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
