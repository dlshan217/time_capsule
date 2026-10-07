from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Memory

class MemoryAdminForm(forms.ModelForm):
    secret_key = forms.CharField(
        required=False,
        min_length=10,
        max_length=128,
        strip=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Set or replace a key (at least 10 characters). Leave blank to keep the existing key.",
    )

    class Meta:
        model = Memory
        fields = "__all__"

    def save(self, commit=True):
        memory = super().save(commit=False)
        secret_key = self.cleaned_data.get("secret_key")
        if secret_key:
            memory.secret_key_hash = make_password(secret_key)
        if commit:
            memory.save()
            self.save_m2m()
        return memory

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    form = MemoryAdminForm
    list_display = ('id', 'title', 'unlock_at', 'created_at', 'is_unlocked')
    list_filter = ('unlock_at', 'created_at')
    search_fields = ('title', 'text')
    ordering = ('-created_at',)
