# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Server State & Admin Controls ---
    # GET: Returns current mode (setup/event) and active event.
    # POST (Admin only): Changes mode or sets the active event.
    path('state/', views.server_state_view, name='server_state'),
    
    # --- Setup Manager Endpoints ---
    # Used during 'setup' mode to configure the show.
    path('shows/', views.show_list_create, name='show_list_create'),
    path('shows/<int:show_id>/events/', views.event_list_create, name='event_list_create'),
    path('shows/<int:show_id>/contestants/', views.contestant_list_create, name='contestant_list_create'),
    
    # --- Score Keeper Endpoints ---
    # POST: Submit a score for a contestant (Requires 'event' mode)
    path('scores/submit/', views.submit_score, name='submit_score'),
    
    # --- Score Display Endpoints ---
    # GET: Returns the calculated standings for a specific event
    path('events/<int:event_id>/standings/', views.event_standings, name='event_standings'),

    path('state/active-contestants/', views.active_event_contestants, name='active_event_contestants'),

    # Add Groups
    path('shows/<int:show_id>/groups/', views.group_list_create, name='group_list_create'),

    path('events/<int:event_id>/stop/', views.event_stop, name="event_stop"),
]

