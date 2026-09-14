from django import forms

from apps.people.models import Participant
from apps.workshops.models import ClassGroup, ClassGroupStatus


class AdminEnrollmentCreateForm(forms.Form):
    participant = forms.ModelChoiceField(
        label="Participante",
        queryset=Participant.objects.none(),
    )
    class_group = forms.ModelChoiceField(
        label="Turma",
        queryset=ClassGroup.objects.none(),
    )

    def __init__(self, *args, class_group: ClassGroup | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["participant"].queryset = Participant.objects.filter(is_active=True).order_by(
            "full_name"
        )
        classes = ClassGroup.objects.filter(status=ClassGroupStatus.OPEN).order_by(
            "start_date", "code"
        )
        if class_group:
            classes = classes.filter(pk=class_group.pk)
            self.fields["class_group"].initial = class_group
            self.fields["class_group"].disabled = True
        self.fields["class_group"].queryset = classes


class ReasonForm(forms.Form):
    reason = forms.CharField(
        label="Justificativa",
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class OptionalReasonForm(ReasonForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].required = False
        self.fields[
            "reason"
        ].help_text = "Obrigatória apenas para confirmar alguém fora da ordem da lista de espera."


class CancellationForm(ReasonForm):
    def __init__(self, *args, require_reason: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].required = require_reason
        if not require_reason:
            self.fields["reason"].widget = forms.HiddenInput()
