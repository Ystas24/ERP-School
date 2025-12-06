from django.db import models
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=150)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(null=True, blank=True)
    def __str__(self): return self.title
