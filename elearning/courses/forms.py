from django import forms

from .models import Course, CourseMaterial, Feedback


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'description')


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ('title', 'file')


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
