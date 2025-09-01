from django import forms
from django.utils import timezone
from .models import Memory

class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['title', 'text', 'file', 'unlock_at']
        widgets = {
            # Use datetime-local so browser + Flatpickr produce compatible value
            'unlock_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'id': 'unlock_at'}),
        }

    def clean_unlock_at(self):
        unlock_at = self.cleaned_data.get('unlock_at')
        if unlock_at is None:
            raise forms.ValidationError("Please choose an unlock date & time.")
        # convert naive -> aware for validation
        if timezone.is_naive(unlock_at):
            unlock_at = timezone.make_aware(unlock_at, timezone.get_current_timezone())
        if unlock_at <= timezone.now():
            raise forms.ValidationError("Unlock time must be in the future.")
        return unlock_at

    def clean(self):
        data = super().clean()
        if not data.get('text') and not data.get('file'):
            raise forms.ValidationError("Add text or upload a file for the memory.")
        return data
