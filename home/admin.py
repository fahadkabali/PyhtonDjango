from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _
from .models import Question, Choice, Response

# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type')
    search_fields = ('text',)
    list_filter = ('question_type',)
    inlines = [ChoiceInline]

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question')
    search_fields = ('user__username', 'question__text')
    list_filter = ('question', 'user')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Response, ResponseAdmin)

# Customizing the Admin interface
admin.site.site_header = _("CyberSecurity Maturity Assessment Tool")
admin.site.site_title = _("CyberSecurity Maturity Assessment Tool")
admin.site.index_title = _("By Milima Security")

# Optionally, you can define custom admin URLs if needed
# This is an example, you might not need custom URLs for your current setup
def custom_admin_view(request):
    return HttpResponse("This is a custom admin view.")

urlpatterns = [
    path('custom_view/', admin.site.admin_view(custom_admin_view), name='custom_admin_view'),
]
