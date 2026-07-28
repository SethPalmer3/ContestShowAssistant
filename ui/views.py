from django.shortcuts import render
from django.db.models import F
from core.models import Contestant, ContestantGroup, Event, Show
from state.models import ServerState
# from django.contrib.auth.decorators import login_required

# @login_required
def setup_dashboard(request):
    # Only returns the HTML shell. The JS inside will fetch the actual data.
    return render(request, 'ui/setup.html')

# @login_required
def score_keeper(request):
    server_state = ServerState.get_state()
    event = server_state.current_event
    all_contestants = None
    contestant_display_names = []
    context = {}
    active_event = server_state.current_event
    if event.group_size == 1 :
        all_contestants = active_event.registered_contestants.all().order_by('show_number').annotate(display_name=F("name"))
    else:
        all_contestants = ContestantGroup.objects.filter(events=active_event).prefetch_related("members")
    if event.group_size > 1:
        for contestant_group in all_contestants:
            member_names = ''
            for member in contestant_group.members.all():
                member_names += f"{member.name}, "
            contestant_display_names.append(member_names[:-2])

    context = {
        'contestants': all_contestants,
        'is_group':  str(event.group_size > 1).lower(),
        'is_completed': server_state.current_event.is_completed,
        'is_finalized': server_state.current_event.is_finalized
    }


    return render(request, 'ui/score_keeper_all.html', context)

def score_display(request):
    # Might not need login if you want this to be a public screen
    return render(request, 'ui/display.html')

def admin_panel(request):
    return render(request, "ui/admin_panel.html")
