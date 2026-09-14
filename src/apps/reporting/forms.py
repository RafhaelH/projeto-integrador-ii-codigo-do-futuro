from django import forms

from apps.accounts.models import UserRole
from apps.workshops.models import ClassGroupStatus, Workshop


class ReportingFilterForm(forms.Form):
    period_start = forms.DateField(
        label="Turmas iniciadas a partir de",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    period_end = forms.DateField(
        label="Turmas iniciadas até",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    workshop = forms.ModelChoiceField(
        label="Oficina",
        queryset=Workshop.objects.none(),
        required=False,
        empty_label="Todas as oficinas",
    )
    class_status = forms.ChoiceField(
        label="Situação da turma",
        required=False,
        choices=[("", "Todas as situações"), *ClassGroupStatus.choices],
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        workshops = Workshop.objects.all()
        if user.role == UserRole.INSTRUCTOR:
            workshops = workshops.filter(
                class_groups__instructor_links__instructor__user=user,
                class_groups__instructor_links__instructor__is_active=True,
            )
        self.fields["workshop"].queryset = workshops.distinct().order_by("title")

    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get("period_start")
        period_end = cleaned_data.get("period_end")
        if period_start and period_end and period_start > period_end:
            raise forms.ValidationError("A data inicial não pode ser posterior à data final.")
        return cleaned_data
