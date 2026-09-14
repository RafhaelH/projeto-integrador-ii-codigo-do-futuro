from django import forms
from django.forms import formset_factory

from .models import AttendanceStatus


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
