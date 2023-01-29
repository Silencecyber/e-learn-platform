from django.contrib import admin
from plattform.models import Got,Profile,Course,Module,Topic,Subscriber,Quiz,Question,Answer,QuizResult

# Register your models here.
admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Topic)
admin.site.register(Subscriber)

admin.site.register(Quiz)

class AnswerInline(admin.TabularInline):
    model=Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines=[AnswerInline]


admin.site.register(Got)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer)
admin.site.register(QuizResult)