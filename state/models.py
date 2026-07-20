from typing import Self

from django.db import models
from django.contrib.auth.models import User
from core.models import Show, Event

"""
The consistant state of the main orchistration server
"""
class ServerState(models.Model):
    """Singleton model to hold the current state of the application."""
    class Mode(models.TextChoices):
        SETUP = 'SETUP', 'Setup Mode'
        EVENT = 'EVENT', 'Event Mode'
        IDLE = 'IDLE', 'Idle'

    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.IDLE) # Current server mode
    current_show = models.ForeignKey(Show, on_delete=models.SET_NULL, null=True, blank=True) # Active Show
    current_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True) # Active event in show

    def save(self, *args, **kwargs):
        self.pk = 1 # Forces this to act as a singleton
        super().save(*args, **kwargs)

    """
    Get the current state of the server.
    Returns the singleton object
    """
    @classmethod
    def get_state(cls) -> Self:
        obj, created = cls.objects.get_or_create(pk=1) # Get the singleton ServerState object
        return obj

"""
Active client roles
"""
class ClientRole(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SCORE_KEEPER = 'SCORE_KEEPER', 'Score Keeper'
        SETUP_MANAGER = 'SETUP_MANAGER', 'Setup Manager'
        SCORE_DISPLAY = 'SCORE_DISPLAY', 'Score Display'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_profile') # Connect to one and only one user
    role = models.CharField(max_length=20, choices=Role.choices)
