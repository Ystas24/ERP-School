from django import forms
from .models import Grade

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["student", "subject", "value"]
        widgets = {
            "value": forms.NumberInput(attrs={"min": 1, "max": 12}),
        }
