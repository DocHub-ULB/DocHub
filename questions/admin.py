from django.contrib import admin
from reversion.admin import VersionAdmin

from questions.models import Question, Answer, Vote

@admin.register(Question)
class QuestionAdmin(VersionAdmin, admin.ModelAdmin):
    pass

@admin.register(Answer)
class AnswerAdmin(VersionAdmin, admin.ModelAdmin):
    pass

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass
