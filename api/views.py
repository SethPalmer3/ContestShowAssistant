from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from state.models import ServerState, ClientRole
from core.models import Show, Event, Contestant, Score, ContestantGroup
from core.services import get_event_standings

# --- Server State & Admin Controls ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def server_state_view(request):
    state = ServerState.get_state()
    
    if request.method == 'GET':
        return Response({ # REST API response
            "mode": state.mode,
            "current_show_id": state.current_show.id if state.current_show else None,
            "current_show": state.current_show.name if state.current_show else None,
            "current_event_id": state.current_event.id if state.current_event else None,
            "current_event": state.current_event.name if state.current_event else None,
            "current_event_group_size": state.current_event.group_size if state.current_event else 1,
            # Add this line so the UI knows if the event is done:
            "event_completed": state.current_event.is_completed if state.current_event else False
        })
        
    elif request.method == 'POST':
        # Ensure only Admins can change the state
        if request.user.role_profile.role != ClientRole.Role.ADMIN:
            return Response({"error": "Only admins can change server state."}, status=403)
            
        # Example of updating mode
        new_mode = request.data.get('mode')
        if new_mode in dict(ServerState.Mode.choices):
            state.mode = new_mode
            state.save()
            return Response({"status": "State updated", "mode": state.mode})
        return Response({"error": "Invalid mode"}, status=400)


"""
GET: fetch a list of contestants for a show
POST: 
"""
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def contestant_list_create(request, show_id):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        return Response({"error": "Show not found"}, status=404)

    if request.method == 'GET':
        # Use prefetch_related to grab the events efficiently
        contestants = Contestant.objects.filter(show=show).prefetch_related('events')
        data = [
            {
                "id": c.id,
                "name": c.name,
                "show_number": c.show_number,
                "events": list(c.events.values_list('id', flat=True)) # Pass enrolled events to the frontend
            } for c in contestants
        ]
        return Response(data)

    elif request.method == 'POST':
        user_role = request.user.role_profile.role
        if user_role not in [ClientRole.Role.ADMIN, ClientRole.Role.SETUP_MANAGER]:
            return Response({"error": "Unauthorized role."}, status=403)
        contestant_name = request.data.get('name')
        show_number = request.data.get('show_number')
        event_ids = request.data.get('events', []) # Get the list of selected event IDs

        if not contestant_name or not show_number:
            return Response({"error": "Name and show number are required."}, status=400)

        try:
            contestant = Contestant.objects.create(
                show=show,
                name=contestant_name,
                show_number=show_number
            )
            # Link the selected events to the new contestant
            if event_ids:
                contestant.events.set(event_ids)
            return Response({"status": f"Added #{show_number} {contestant_name}", "id": contestant.id}) # Success of contestant creation
        except Exception as e:
            return Response({"error": "Could not create contestant. Make sure the show number is unique."}, status=400)


# --- Setup Manager Endpoints ---

"""
List of shows
"""
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def show_list_create(request):
    if request.method == 'GET':
        shows = Show.objects.all().values('id', 'name', 'date')
        return Response(list(shows))
    
    # POST logic would go here (Requires Setup Manager or Admin)
    return Response({"message": "Show creation endpoint ready."})

"""
Get a list of events tied to a given show id
"""
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_list_create(request, show_id):
    if request.method == 'GET':
        events = Event.objects.filter(show_id=show_id).values()
        return Response(list(events))
    
    return Response({"message": "Event creation endpoint ready."})

# --- Score Keeper Endpoints ---

"""
Submitting a score for a contestant(s)
for a given event
"""
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_score(request):
    state = ServerState.get_state()
    user_role = request.user.role_profile.role
    
    if state.mode != ServerState.Mode.EVENT: # Ensure scores are submitted while events are occuring
        return Response({"error": "Scores can only be submitted in Event Mode."}, status=403)
    
    if user_role not in [ClientRole.Role.ADMIN, ClientRole.Role.SCORE_KEEPER]: # Permission check
        return Response({"error": "Unauthorized role."}, status=403)

    entity_id = request.data.get('entity_id')
    is_group = request.data.get('is_group', False)
    submitted_score_value = request.data.get('value')
    is_tie_breaker = request.data.get('is_tie_breaker', False)

    try:
        from django.db import transaction
        with transaction.atomic():
            if is_group:
                # Find the group and score every member inside it
                group = ContestantGroup.objects.get(id=entity_id)
                for contestant in group.members.all():
                    Score.objects.create(
                        event=state.current_event,
                        contestant=contestant,
                        value=submitted_score_value,
                        is_tie_breaker=is_tie_breaker,
                        submitted_by=request.user
                    )
            else:
                # Score an individual
                contestant = Contestant.objects.get(id=entity_id)
                Score.objects.create(
                    event=state.current_event,
                    contestant=contestant,
                    value=submitted_score_value,
                    is_tie_breaker=is_tie_breaker,
                    submitted_by=request.user
                )
        return Response({"status": "Score saved successfully"})
        
    except (Contestant.DoesNotExist, ContestantGroup.DoesNotExist):
        return Response({"error": "Entity not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# --- Score Display Endpoints ---

"""
Get the scores of a specific event
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_standings(request, event_id):
    try:
        # The service now returns a fully formatted list of dictionaries, 
        # so we can just pass it directly to the Response.
        standings = get_event_standings(event_id)
        return Response(standings)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

"""
Return the contestants or groups of the active event
"""
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_event_contestants(request):
    state = ServerState.get_state()
    
    if state.mode != ServerState.Mode.EVENT or not state.current_event:
        return Response({"error": "Server is not currently in Event mode."}, status=400)
    
    active_event = state.current_event
    
    # If it's a group event, return the predefined ContestantGroups
    if active_event.group_size > 1:
        groups = ContestantGroup.objects.filter(events=active_event)
        data = []
        for g in groups:
            # Create a string of member names so the scorekeeper knows exactly who is in the group
            member_names = ", ".join([c.name for c in g.members.all()])
            data.append({
                "id": g.id,
                "label": f"{g.name} ({member_names})",
                "is_group": True
            })
        return Response(data)
        
    # Otherwise, return individual contestants
    else:
        contestants = active_event.registered_contestants.all().order_by('show_number')
        data = [
            {
                "id": c.id, 
                "label": f"#{c.show_number} - {c.name}",
                "is_group": False
            } 
            for c in contestants
        ]
        return Response(data)

"""
Get or create groups of contestants for a event
for a specific show
"""
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_list_create(request, show_id):
    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        return Response({"error": "Show not found"}, status=404)

    if request.method == 'GET':
        groups = ContestantGroup.objects.filter(show=show)
        data = [
            {
                "id": g.id, 
                "name": g.name, 
                "members": [m.name for m in g.members.all()]
            } for g in groups
        ]
        return Response(data)
        
    elif request.method == 'POST':
        user_role = request.user.role_profile.role
        if user_role not in [ClientRole.Role.ADMIN, ClientRole.Role.SETUP_MANAGER]: # Permission check
            return Response({"error": "Unauthorized role."}, status=403)
            
        group_name = request.data.get('name')
        group_member_ids = request.data.get('members', [])
        event_ids = request.data.get('events', [])
        
        if not group_name:
            return Response({"error": "Group name is required."}, status=400)
            
        if not event_ids:
            return Response({"error": "You must assign the group to at least one event."}, status=400)
            
        try:
            # Validate the group size against the selected events
            events = Event.objects.filter(id__in=event_ids)
            for event in events:
                if event.group_size <= 1:
                    return Response({"error": f"Event '{event.name}' does not allow groups."}, status=400)
                if len(group_member_ids) != event.group_size:
                    return Response(
                        {"error": f"Event '{event.name}' requires exactly {event.group_size} members, but you selected {len(group_member_ids)}."}, 
                        status=400
                    )
                for member_id in group_member_ids:
                    if not event.registered_contestants.filter(id=member_id).exists():
                        return Response({"error": "All group members must be individually registered for the selected events first."}, status=400)
            
            # If validation passes, create the group
            created_group = ContestantGroup.objects.create(show=show, name=group_name)
            
            if group_member_ids:
                created_group.members.set(group_member_ids)
            if event_ids:
                created_group.events.set(event_ids)
                
            return Response({"status": f"Created group: {group_name}"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
