from django.contrib import admin
from django.utils.html import format_html
from django.urls.base import reverse
from django.shortcuts import redirect
from . import models


class Matura_Anwser_Inline(admin.TabularInline):
    model = models.Matura_Anwser


class Matura_Question_Inline(admin.TabularInline):
    model = models.Matura_Question
    show_change_link = True
    extra = 0

class Matura_Task_Inline(admin.TabularInline):
    model = models.Matura_Task
    show_change_link = True
    extra = 0

@admin.register(models.Matura_Task)
class MaturaTask(admin.ModelAdmin):
    readonly_fields = ('category_link',)
    inlines = [
        Matura_Question_Inline,
    ]

    def response_change(self, request, obj):
        result = super(MaturaTask, self).response_change(request, obj)
        # it allows me to easily get redirected back to the page-view if I edited it from the page-view
        if "next" in request.GET:
            return redirect(request.GET['next'])
        return result

    def category_link(self, obj):
        url = reverse("admin:{}_{}_change".format(obj.category._meta.app_label, obj.category._meta.model_name),
                      args=(obj.category.id,))
        return format_html('<a href="{}">Edit the category</a>'.format(url))


@admin.register(models.Matura_Question)
class MaturaQuestion(admin.ModelAdmin):
    readonly_fields = ('task', 'task_link')

    def task_link(self, obj):
        url = reverse("admin:{}_{}_change".format(obj.task._meta.app_label, obj.task._meta.model_name),
                      args=(obj.task.id,))
        return format_html('<a href="{}">Edit the task</a>'.format(url))

    inlines = [
        Matura_Anwser_Inline,
    ]
@admin.register(models.Matura_Category)
class MaturaCategory(admin.ModelAdmin):
    prepopulated_fields = {'slug_url': ('year', 'level', 'month')}
    inlines = [
        Matura_Task_Inline,
    ]