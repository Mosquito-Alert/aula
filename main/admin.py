from django.contrib import admin

# Register your models here.

from .models import *


class QuestionLinkInline(admin.TabularInline):
    model = Question
    fields = ('question_order', 'text', 'doc_link', 'question_picture')
    show_change_link = True


class AnswerInline(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline,]


class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'html_header', 'published', 'type_text', 'campaign')
    search_fields = ('author__username', 'name', 'campaign__name')
    inlines = [ QuestionLinkInline, ]


class QuizRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'taken_by', 'quiz', 'date','date_finished','run_number')
    search_fields = ('taken_by__username', 'quiz__name', 'date','date_finished')


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ( 'user__username', )


class EducationCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign',)
    search_fields = ('name', 'campaign__name', )


admin.site.register(EducationCenter, EducationCenterAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizRun, QuizRunAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Campaign)
admin.site.register(Profile, ProfileAdmin)
#admin.site.register(GroupAnswer)
