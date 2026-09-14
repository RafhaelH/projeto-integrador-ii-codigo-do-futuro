from django import forms
from django.db.models import Q

from apps.people.models import Institution, Instructor

from .models import ClassGroup, ClassInstructor, Meeting, Workshop, WorkshopStatus


class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ("title", "slug", "summary", "objective", "syllabus", "estimated_hours")
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "objective": forms.Textarea(attrs={"rows": 4}),
            "syllabus": forms.Textarea(attrs={"rows": 5}),
            "estimated_hours": forms.NumberInput(attrs={"min": "0.01", "step": "0.5"}),
        }


class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = (
            "workshop",
            "institution",
            "code",
            "title",
            "location",
            "capacity",
            "waitlist_enabled",
            "registration_opens_at",
            "registration_closes_at",
            "start_date",
            "end_date",
        )
        widgets = {
            "registration_opens_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "registration_closes_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "capacity": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        workshops = Workshop.objects.filter(status=WorkshopStatus.PUBLISHED)
        institutions = Institution.objects.filter(is_active=True)
        if self.instance.pk:
            workshops = Workshop.objects.filter(
                Q(status=WorkshopStatus.PUBLISHED) | Q(pk=self.instance.workshop_id)
            )
            if self.instance.institution_id:
                institutions = Institution.objects.filter(
                    Q(is_active=True) | Q(pk=self.instance.institution_id)
                )
        self.fields["workshop"].queryset = workshops.order_by("title")
        self.fields["institution"].queryset = institutions.order_by("name")


class ClassInstructorForm(forms.ModelForm):
    class Meta:
        model = ClassInstructor
        fields = ("instructor", "is_lead")

    def __init__(self, *args, class_group: ClassGroup, **kwargs):
        self.class_group = class_group
        super().__init__(*args, **kwargs)
        linked = class_group.instructor_links.values_list("instructor_id", flat=True)
        self.fields["instructor"].queryset = (
            Instructor.objects.filter(is_active=True).exclude(pk__in=linked).select_related("user")
        )
        if class_group.instructor_links.filter(is_lead=True).exists():
            self.fields["is_lead"].disabled = True
            self.fields["is_lead"].help_text = "A turma já possui um instrutor principal."


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ("title", "description", "starts_at", "ends_at")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, class_group: ClassGroup | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_group is not None:
            self.instance.class_group = class_group
