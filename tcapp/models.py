from django.db import models
from django.utils import timezone

class Memory(models.Model):
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='memories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unlock_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Memory {self.pk}"

    @property
    def is_unlocked(self):
        """
        Return True if current time (timezone-aware) is >= unlock_at.
        Handles naive unlock_at by making it aware in current timezone.
        """
        now = timezone.now()
        unlock = self.unlock_at
        try:
            if timezone.is_naive(unlock):
                unlock = timezone.make_aware(unlock, timezone.get_current_timezone())
        except Exception:
            # if something odd, fallback to comparing directly
            pass
        return bool(unlock and now >= unlock)
