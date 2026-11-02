from django.contrib import admin

from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "id")
    search_fields = ("title", "description")
    list_filter = ("owner",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "id")
    search_fields = ("title", "description")
    list_filter = ("course",)
