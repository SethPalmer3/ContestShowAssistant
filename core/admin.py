from django.contrib import admin
from .models import Show, Event, Contestant, Score, ContestantGroup

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Add 'sequence_order' here if you added it to the model above
    list_display = ('name', 'show', 'score_type', 'group_size', 'score_processor', 'is_completed')
    list_filter = ('show', 'is_completed')
    ordering = ('show', 'name') # Or ('show', 'sequence_order')

@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    list_display = ('id', 'show_number', 'name', 'show')
    list_filter = ('show',)
    search_fields = ('name', 'show_number')
    # This creates a nice dual-list widget for adding contestants to events
    filter_horizontal = ('events',) 

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('contestant', 'event', 'value', 'submitted_by', 'timestamp')
    list_filter = ('event', 'contestant__show')
    # Allows the admin to easily edit existing scores if a mistake was made
    list_editable = ('value',)


@admin.register(ContestantGroup)
class ContestantGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'show')
    list_filter = ('show',)
    filter_horizontal = ('members', 'events') # Gives you the nice drag-and-drop UI
