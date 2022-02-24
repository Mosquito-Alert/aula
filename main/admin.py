from django.contrib import admin

# Register your models here.

from .models import *

class QuizRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'taken_by', 'quiz', 'date','date_finished','run_number')
    search_fields = ('taken_by__username', 'quiz__name', 'date','date_finished')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'html_header', 'published', 'type_text')
    search_fields = ('author__username', 'name', 'type_text')

admin.site.register(EducationCenter)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizRun, QuizRunAdmin)
admin.site.register(Question)
admin.site.register(Campaign)
#admin.site.register(GroupAnswer)
