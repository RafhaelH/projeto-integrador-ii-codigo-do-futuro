from django import forms
from django.forms import formset_factory
from django.utils import timezone

from .models import AttendanceStatus, Evaluation, StudentProject


class AttendanceEntryForm(forms.Form):
    enrollment_id = forms.UUIDField(widget=forms.HiddenInput())
    participant_name = forms.CharField(label="Participante", disabled=True)
    status = forms.ChoiceField(label="Situação", choices=AttendanceStatus.choices)
    note = forms.CharField(
        label="Justificativa ou observação",
        max_length=255,
        required=False,
    )


AttendanceFormSet = formset_factory(
    AttendanceEntryForm,
    extra=0,
    min_num=1,
    validate_min=True,
)


class StudentProjectForm(forms.ModelForm):
    repository_url = forms.URLField(
        label="Repositório",
        required=False,
        assume_scheme="https",
    )
    demonstration_url = forms.URLField(
        label="Demonstração",
        required=False,
        assume_scheme="https",
    )

    class Meta:
        model = StudentProject
        fields = (
            "title",
            "description",
            "repository_url",
            "demonstration_url",
            "is_delivered",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("is_delivered") and not self.instance.delivered_at:
            self.instance.delivered_at = timezone.now()
        elif not cleaned_data.get("is_delivered"):
            self.instance.delivered_at = None
        return cleaned_data


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = StudentProject
        fields = ("review_notes",)
        widgets = {"review_notes": forms.Textarea(attrs={"rows": 6})}


class EvaluationForm(forms.ModelForm):
    publish = forms.BooleanField(
        label="Publicar resultado para o participante",
        required=False,
    )

    class Meta:
        model = Evaluation
        fields = ("final_score", "feedback")
        widgets = {
            "final_score": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.1"}),
            "feedback": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["publish"].initial = self.instance.published_at is not None
