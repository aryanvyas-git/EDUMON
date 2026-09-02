from django.contrib import admin

from .models import Course, CourseMaterial, Enrolment, Feedback


class EnrolmentInline(admin.TabularInline):
    model = Enrolment
    extra = 0


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    list_filter = ('teacher',)
    search_fields = ('title', 'description')
    inlines = [EnrolmentInline, CourseMaterialInline]


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_blocked')
    list_filter = ('is_blocked', 'course')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('course', 'rating')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')
    list_filter = ('course',)
