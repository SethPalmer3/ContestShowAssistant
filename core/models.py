from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User

"""
Single show data
"""
class Show(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.date})"

"""
Single Event data
Events are tied to specific shows
"""
class Event(models.Model):
    class ScoreType(models.TextChoices):
        TIME = 'TIME', _('Time')
        POINTS = 'POINTS', _('Points')

    class ScoreOrder(models.TextChoices):
        ASC = 'ASC', _('Ascending (Lowest is best)')
        DESC = 'DESC', _('Descending (Highest is best)')

    class ScoreProcessor(models.TextChoices):
        SUM = 'SUM', _('Sum')
        AVG = 'AVG', _('Average')
        MAX = 'MAX', _('Maximum')

    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='events')
    sequence_order = models.IntegerField(default=0, help_text="Order in which the event occurs in the show")   
    name = models.CharField(max_length=255)
    group_size = models.IntegerField(default=1, help_text="Number of contestants scored together (1 for individual)")
    score_type = models.CharField(max_length=10, choices=ScoreType.choices)
    score_order = models.CharField(max_length=10, choices=ScoreOrder.choices, help_text="How to sort the results of multiple scores")
    score_processor = models.CharField(max_length=10, choices=ScoreProcessor.choices, help_text="How to combine multiple scores")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name.__str__()

"""
A contestant for a specific show
"""
class Contestant(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='contestants')
    name = models.CharField(max_length=255)
    show_number = models.IntegerField()
    events = models.ManyToManyField(Event, related_name='registered_contestants')

    class Meta:
        unique_together = ('show', 'show_number')

    def __str__(self):
        return f"#{self.show_number} {self.name}"

"""
Individual scores for a contestant or group of contestants
for one event for one show
"""
class Score(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='scores')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='scores')
    value = models.FloatField()
    is_tie_breaker = models.BooleanField(default=False)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tb_flag = " (Tie-Breaker)" if self.is_tie_breaker else ""
        return f"{self.contestant.name} - {self.event.name}: {self.value}{tb_flag}"

"""
A group of contestants for events that need 
a group of contestants
"""
class ContestantGroup(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='contestant_groups')
    name = models.CharField(max_length=255, help_text="e.g., 'Team Alpha' or 'Pair 1'")
    members = models.ManyToManyField(Contestant, related_name='group_memberships')
    events = models.ManyToManyField(Event, related_name='registered_groups')

    @property
    def display_name(self):
        # Joins the names of all members in the format: 'name1, name2, ...'
        return ", ".join(member.name for member in self.members.all())


    def __str__(self):
        return f"{self.name} ({self.show.name})"
