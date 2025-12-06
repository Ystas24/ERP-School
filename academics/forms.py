from django import forms
from .models import Homework, Subject

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ["title", "text", "subject", "classroom", "deadline"]

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher", None)
        super().__init__(*args, **kwargs)
        # якщо в системі вчитель — показуємо тільки його предмети
        if teacher is not None:
            self.fields["subject"].queryset = Subject.objects.filter(teacher=teacher)
