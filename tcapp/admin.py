from django.contrib import admin
from .models import Memory

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'unlock_at', 'created_at', 'is_unlocked')
    list_filter = ('unlock_at', 'created_at')
    search_fields = ('title', 'text')
    ordering = ('-created_at',)
